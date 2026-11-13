"""Backend OpenAI API client and connection helper for FinWiseIQ."""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client() -> OpenAI:
    """Return an authenticated OpenAI client using environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise RuntimeError(
            "OPENAI_API_KEY is missing or still set to the placeholder value in .env."
        )
    return OpenAI(api_key=api_key, timeout=30)


def get_model_name() -> str:
    """Return the configured OpenAI model ID from environment variables."""
    model = os.getenv("OPENAI_MODEL", "").strip()
    if not model:
        raise RuntimeError("OPENAI_MODEL is not configured in the environment.")
    return model


def test_connection() -> str:
    """Send a minimal request to verify OpenAI API connectivity."""
    client = get_openai_client()
    model = get_model_name()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with OK only."}],
    )
    return (response.choices[0].message.content or "").strip()


if __name__ == "__main__":
    print("OpenAI API connection status:", test_connection())
