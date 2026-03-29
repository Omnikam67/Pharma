import json
import os
import re
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.translation_service import translate_text

router = APIRouter(prefix="/report", tags=["Report Analysis"])


class ReportAnalyzeRequest(BaseModel):
    image: str
    language: Optional[str] = "en"


class ReportAskRequest(BaseModel):
    session_id: str
    question: str
    language: Optional[str] = "en"


REPORT_SESSION_TTL_HOURS = 6
REPORT_SESSIONS: dict[str, dict] = {}
REPORT_SESSIONS_FILE = Path(__file__).resolve().parents[2] / "report_sessions.json"


def _utc_now() -> datetime:
    return datetime.utcnow()


def _cleanup_report_sessions() -> None:
    cutoff = _utc_now() - timedelta(hours=REPORT_SESSION_TTL_HOURS)
    stale_keys = [k for k, v in REPORT_SESSIONS.items() if v.get("updated_at") and v["updated_at"] < cutoff]
    for key in stale_keys:
        REPORT_SESSIONS.pop(key, None)
    if stale_keys:
        _save_report_sessions()


def _serialize_session(session: dict) -> dict:
    out = dict(session or {})
    created_at = out.get("created_at")
    updated_at = out.get("updated_at")
    out["created_at"] = created_at.isoformat() if isinstance(created_at, datetime) else created_at
    out["updated_at"] = updated_at.isoformat() if isinstance(updated_at, datetime) else updated_at
    return out


def _deserialize_session(session: dict) -> dict:
    out = dict(session or {})
    for key in ("created_at", "updated_at"):
        val = out.get(key)
        if isinstance(val, str):
            try:
                out[key] = datetime.fromisoformat(val)
            except Exception:
                out[key] = _utc_now()
        elif not isinstance(val, datetime):
            out[key] = _utc_now()
    if not isinstance(out.get("history"), list):
        out["history"] = []
    if not isinstance(out.get("structured"), dict):
        out["structured"] = {}
    return out


def _save_report_sessions() -> None:
    try:
        payload = {sid: _serialize_session(sess) for sid, sess in REPORT_SESSIONS.items()}
        REPORT_SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        REPORT_SESSIONS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _load_report_sessions() -> None:
    if not REPORT_SESSIONS_FILE.exists():
        return
    try:
        raw = REPORT_SESSIONS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            return
        REPORT_SESSIONS.clear()
        for sid, sess in data.items():
            if isinstance(sid, str) and isinstance(sess, dict):
                REPORT_SESSIONS[sid] = _deserialize_session(sess)
    except Exception:
        return


def _to_english_if_needed(text: str, language: str) -> str:
    if not text:
        return ""
    lang = (language or "en").lower()
    if lang == "en":
        return text
    translated = translate_text(text, target="en")
    return translated if translated else text


_load_report_sessions()


async def _translate_with_groq_fallback(text: str, target_lang: str, api_key: str) -> str:
    if not text:
        return text
    lang = (target_lang or "en").lower()
    if lang == "en":
        return text

    mapped = {"hi": "Hindi", "mr": "Marathi", "en": "English"}
    language_name = mapped.get(lang, lang)
    prompt = (
        f"Translate the following medical explanation to {language_name}. "
        "Preserve medical values, numbers, and bullet formatting. "
        "Return only translated text.\n\n"
        f"{text}"
    )
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            payload = {
                "model": os.getenv("GROQ_CHAT_MODEL", "").strip() or "llama-3.3-70b-versatile",
                "temperature": 0,
                "max_tokens": 900,
                "messages": [
                    {"role": "system", "content": "You are a precise medical translator."},
                    {"role": "user", "content": prompt},
                ],
            }
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code >= 400:
                return text
            translated = (
                resp.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return translated or text
    except Exception:
        return text


def _extract_json(text: str) -> dict:
    if not text:
        return {}
    raw = text.strip()
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def _build_markdown_report(data: dict) -> str:
    summary = str(data.get("summary") or "Could not confidently read enough report details.")
    findings = data.get("findings") or []
    abnormal_flags = data.get("abnormal_flags") or []
    next_steps = data.get("next_steps") or []
    uncertainty = str(data.get("uncertainty_note") or "This is an educational explanation, not a diagnosis.")

    lines = [
        "### Medical Report Explanation",
        "",
        f"**Simple Summary:** {summary}",
        "",
        "**Key Findings (from visible report text):**",
    ]
    if findings:
        for item in findings:
            lines.append(f"- {item}")
    else:
        lines.append("- No clear structured findings could be extracted.")

    lines.append("")
    lines.append("**Possible Abnormal / Attention Points:**")
    if abnormal_flags:
        for item in abnormal_flags:
            lines.append(f"- {item}")
    else:
        lines.append("- No obvious abnormal marker detected from visible text.")

    lines.append("")
    lines.append("**What To Discuss With Your Doctor:**")
    if next_steps:
        for item in next_steps:
            lines.append(f"- {item}")
    else:
        lines.append("- Please share this report with your doctor for confirmed interpretation.")

    lines.append("")
    lines.append(f"**Note:** {uncertainty}")
    return "\n".join(lines)


@router.post("/analyze")
async def analyze_report(request: ReportAnalyzeRequest):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"success": False, "message": "Report analysis unavailable (missing GROQ_API_KEY)."}

    data_url = (request.image or "").strip()
    if not data_url:
        return {"success": False, "message": "No report image provided."}
    if not data_url.startswith("data:image"):
        data_url = f"data:image/jpeg;base64,{data_url}"

    configured_model = os.getenv("GROQ_VISION_MODEL", "").strip()
    model_candidates = [
        m
        for m in [
            configured_model,
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision-preview",
        ]
        if m
    ]

    prompt = (
        "You are a careful medical report explainer for patients.\n"
        "Read only what is clearly visible in the uploaded report image.\n"
        "Do not invent values or diagnoses.\n"
        "If text is unclear, explicitly mention uncertainty.\n"
        "Return only JSON with keys:\n"
        "summary (string), findings (array of strings), abnormal_flags (array of strings), "
        "next_steps (array of strings), uncertainty_note (string)."
    )

    content = ""
    last_error = ""
    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            for model_name in model_candidates:
                payload = {
                    "model": model_name,
                    "temperature": 0,
                    "max_tokens": 700,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Explain this medical report in simple patient-friendly language using only visible data."},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        },
                    ],
                }
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if resp.status_code >= 400:
                    last_error = resp.text
                    continue
                content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    break
    except Exception as e:
        return {"success": False, "message": f"Failed to analyze report image: {str(e)}"}

    if not content:
        return {
            "success": False,
            "message": "Vision model request failed. Set GROQ_VISION_MODEL to a model your key can access.",
            "error": last_error[:220],
        }

    parsed = _extract_json(content)
    if not parsed:
        parsed = {
            "summary": "Could not parse structured analysis from model output.",
            "findings": [],
            "abnormal_flags": [],
            "next_steps": ["Please re-upload a clearer report image and consult your doctor."],
            "uncertainty_note": "Model output was not in expected format.",
        }

    message = _build_markdown_report(parsed)
    lang = (request.language or "en").lower()
    if lang != "en":
        translated = translate_text(message, target=lang)
        # If external translation is unavailable, fall back to Groq translation.
        if not translated or translated.strip() == message.strip():
            translated = await _translate_with_groq_fallback(message, lang, api_key)
        message = translated

    _cleanup_report_sessions()
    report_session_id = str(uuid.uuid4())
    REPORT_SESSIONS[report_session_id] = {
        "structured": parsed,
        "history": [],
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _save_report_sessions()

    return {
        "success": True,
        "message": message,
        "structured": parsed,
        "report_session_id": report_session_id,
    }


@router.post("/chat")
async def chat_on_report(request: ReportAskRequest):
    _cleanup_report_sessions()
    session_id = (request.session_id or "").strip()
    if not session_id:
        return {"success": False, "message": "Missing report session id."}

    session = REPORT_SESSIONS.get(session_id)
    if not session:
        return {"success": False, "message": "Report session not found or expired. Please re-upload the report."}

    question = (request.question or "").strip()
    if not question:
        return {"success": False, "message": "Please ask a question about the report."}

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"success": False, "message": "Report chat unavailable (missing GROQ_API_KEY)."}

    lang = (request.language or "en").lower()
    question_en = _to_english_if_needed(question, lang)
    report_data = session.get("structured") or {}
    history = session.get("history") or []
    recent_history = history[-8:]

    chat_model_candidates = [
        m
        for m in [
            os.getenv("GROQ_CHAT_MODEL", "").strip(),
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]
        if m
    ]

    system_prompt = (
        "You are a careful medical report Q&A assistant.\n"
        "Answer ONLY from the provided report summary JSON and prior report-chat turns.\n"
        "Do not invent lab values, diagnoses, or recommendations not grounded in that data.\n"
        "If asked something unavailable in report data, clearly say it is not visible in the report.\n"
        "Keep answers concise, patient-friendly, and safety-conscious."
    )

    history_text = "\n".join(
        [f"{item.get('role', 'user')}: {item.get('content', '')}" for item in recent_history if item.get("content")]
    ).strip()
    if not history_text:
        history_text = "No prior questions."

    user_prompt = (
        f"Report JSON:\n{json.dumps(report_data, ensure_ascii=False)}\n\n"
        f"Previous Q&A:\n{history_text}\n\n"
        f"Current Question:\n{question_en}\n\n"
        "Respond in English."
    )

    answer_en = ""
    last_error = ""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for model_name in chat_model_candidates:
                payload = {
                    "model": model_name,
                    "temperature": 0,
                    "max_tokens": 450,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                }
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if resp.status_code >= 400:
                    last_error = resp.text
                    continue
                answer_en = (
                    resp.json()
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                if answer_en:
                    break
    except Exception as e:
        return {"success": False, "message": f"Failed to answer report question: {str(e)}"}

    if not answer_en:
        return {
            "success": False,
            "message": "Could not generate report-based answer right now. Please try again.",
            "error": last_error[:220],
        }

    answer = answer_en
    if lang != "en":
        translated = translate_text(answer_en, target=lang)
        if not translated or translated.strip() == answer_en.strip():
            translated = await _translate_with_groq_fallback(answer_en, lang, api_key)
        if translated:
            answer = translated

    session.setdefault("history", []).append({"role": "user", "content": question_en})
    session.setdefault("history", []).append({"role": "assistant", "content": answer_en})
    session["updated_at"] = _utc_now()
    _save_report_sessions()

    return {
        "success": True,
        "message": answer,
        "session_id": session_id,
    }
