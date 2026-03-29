import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

# Keep local development quiet when Langfuse credentials are not configured.
if not (
    os.getenv("LANGFUSE_PUBLIC_KEY")
    and os.getenv("LANGFUSE_SECRET_KEY")
    and os.getenv("LANGFUSE_HOST")
):
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
