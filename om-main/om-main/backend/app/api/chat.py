from fastapi import APIRouter
from pydantic import BaseModel
from langfuse import observe, get_client
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from app.agents.conversational_agent import parse_user_message
from app.agents.decision_agent import DecisionAgent
from app.agents.memory import get_memory
from app.services.language_detector import LanguageDetector
from app.services.translation_service import translate_text
from app.agents.conversational_agent import llm
from langchain_core.messages import SystemMessage, HumanMessage


def _protect_terms(text: str, terms: list[str]) -> tuple[str, dict[str, str]]:
    if not text or not terms:
        return text, {}
    safe_terms = []
    seen = set()
    for term in terms:
        if not term:
            continue
        t = str(term).strip()
        if not t:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        safe_terms.append(t)
    if not safe_terms:
        return text, {}
    replacements = {}
    out = text
    for idx, term in enumerate(sorted(safe_terms, key=len, reverse=True)):
        token = f"__TERM_{idx}__"
        replacements[token] = term
        out = out.replace(term, token)
    return out, replacements


def _restore_terms(text: str, replacements: dict[str, str]) -> str:
    if not text or not replacements:
        return text
    out = text
    for token, term in replacements.items():
        out = out.replace(token, term)
    return out


def _translate_with_llm(text: str, target: str) -> str:
    if not text:
        return text
    lang_name = {"hi": "Hindi", "mr": "Marathi", "en": "English"}.get(target, target)
    system = (
        "You are a precise translator. Translate the user's text into "
        f"{lang_name}. Preserve tokens like __TERM_0__ exactly. "
        "Return only the translated text."
    )
    try:
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=text)])
        return resp.content or text
    except Exception:
        return text

router = APIRouter(prefix="/chat", tags=["Agent Chat"])

# ✅ Lazy initialization of decision_agent to prevent blocking imports
_decision_agent = None

def get_decision_agent():
    global _decision_agent
    if _decision_agent is None:
        _decision_agent = DecisionAgent()
    return _decision_agent

class ChatRequest(BaseModel):
    message: str
    session_id: str
    image: str = None 
    language: Optional[str] = "en"
    location: Optional[dict] = None

@router.post("")
@observe(name="chat_endpoint")
async def chat(request: ChatRequest):
    # Ensure `.env` is loaded so Langfuse picks up keys when using `get_client()`.
    backend_dir = Path(__file__).resolve().parents[2]
    load_dotenv(backend_dir / ".env", override=False)

    client = get_client()

    # Langfuse client API differs by version. v4 removed `update_current_trace`.
    try:
        if hasattr(client, "update_current_trace"):
            client.update_current_trace(
                session_id=request.session_id,
                user_id="react_frontend_user",
            )
        elif hasattr(client, "update_current_span"):
            client.update_current_span(
                metadata={
                    "session_id": request.session_id,
                    "user_id": "react_frontend_user",
                }
            )
    except Exception:
        # Tracing must never break the endpoint.
        pass

    memory = get_memory(request.session_id)
    history = memory.load_memory_variables({}).get("history", "")

    original_message = request.message
    requested_language = (request.language or "en").lower()
    detected_language, detected_confidence = LanguageDetector.detect_language(original_message)
    language = requested_language
    if requested_language == "en" and detected_language != "en" and detected_confidence >= 0.65:
        language = detected_language

    user_message = original_message
    if language != "en":
        user_message = translate_text(original_message, target="en")
    # Send History + New message to the parser (store/parse in English)
    enriched_message = f"History:\n{history}\n\nCurrent User Message: {user_message}"

    parsed = parse_user_message(enriched_message)

    # forward session_id into decision logic so executions know who is ordering
    result = await get_decision_agent().decide(
        parsed,
        raw_message=original_message,
        session_id=request.session_id,
        image=request.image,
        location=request.location,
    )

    # ✅ FIX: Save the actual readable bot message to memory, not the JSON
    memory.save_context(
        {"input": original_message}, 
        {"output": result.get("message", "")}
    )

    if language != "en":
        result = dict(result)
        msg = result.get("message", "")
        terms = []
        if isinstance(result.get("product_name"), str):
            terms.append(result.get("product_name"))
        receipt = result.get("receipt") or {}
        if isinstance(receipt, dict) and isinstance(receipt.get("medicine"), str):
            terms.append(receipt.get("medicine"))
        protected, repl = _protect_terms(msg, terms)
        translated = translate_text(protected, target=language)
        if translated == protected:
            translated = _translate_with_llm(protected, language)
        result["message"] = _restore_terms(translated, repl)

    return result
