"""FinWiseIQ branded Gradio frontend (KAN-39 visual enhancement).

This is a stand-alone launchable UI that *reuses* app.interface.respond from
PR #18, preserving the original retrieval -> OpenAI -> citations flow.

Run from repository root: python -m app.finwiseiq_redesign
"""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Callable

import gradio as gr

ASSETS = Path(__file__).resolve().parent / "assets"
CSS_FILE = Path(__file__).resolve().parent / "finwiseiq_theme.css"

SUGGESTIONS = (
    "What is Murabahah financing?",
    "What is Islamic banking?",
    "What is Shariah-compliant financing?",
    "What is the difference between Islamic and conventional banking?",
)

# A safe generic message rather than exposing API key, stack trace or user data.
ERROR_MESSAGE = (
    "Sorry, something went wrong while preparing the answer. "
    "Please try again in a moment."
)
EMPTY_MESSAGE = "Please type a question about Islamic finance or Malaysian financial compliance."
WELCOME_MESSAGE = "Welcome to FinWiseIQ! Choose a suggested topic or type your question below."
LOADING_MESSAGE = "Preparing your answer…"
ENGLISH_GREETING = "Hello! How can I help you with Islamic finance or Malaysian financial compliance?"
MALAY_GREETING = "Hai! Ada soalan tentang kewangan Islam atau pematuhan kewangan di Malaysia?"
SALAM_GREETING = (
    "Waalaikumsalam! Ada soalan tentang kewangan Islam atau pematuhan kewangan di Malaysia?"
)
GREETING_RESPONSES = {
    "hi": ENGLISH_GREETING,
    "hello": ENGLISH_GREETING,
    "hai": MALAY_GREETING,
    "salam": SALAM_GREETING,
    "assalamualaikum": SALAM_GREETING,
    "assalamu alaikum": SALAM_GREETING,
}


def _real_responder() -> Callable:
    """Import existing production response handler only when building real app.

    This avoids duplicating backend code or storing API credentials in the UI.
    """
    from app.interface import respond  # noqa: PLC0415 - existing PR #18 function

    return respond


def _assistant_says(message: dict, text: str) -> bool:
    if message["role"] != "assistant":
        return False
    content = message["content"]
    # Gradio can return rendered text as a list of content blocks.
    if isinstance(content, list) and len(content) == 1:
        block = content[0]
        if isinstance(block, dict) and block.get("type") == "text":
            content = block.get("text")
    return content == text


def _append_question(message: str, history: list[dict] | None):
    safe_history = list(history or [])
    question = (message or "").strip()
    if not question:
        if safe_history and _assistant_says(safe_history[-1], EMPTY_MESSAGE):
            return safe_history, ""
        return safe_history + [{"role": "assistant", "content": EMPTY_MESSAGE}], ""

    return safe_history + [{"role": "user", "content": question}], question


def _answer_message(question: str, history: list[dict], responder: Callable) -> dict:
    greeting = " ".join(question.casefold().strip("!?., ").split())
    answer = GREETING_RESPONSES.get(greeting)
    if answer is None:
        try:
            answer = responder(question, history)
            if not isinstance(answer, str):
                answer = str(answer) if answer is not None else ERROR_MESSAGE
        except Exception:
            # Keep API keys and technical details out of user-facing errors.
            answer = ERROR_MESSAGE

    return {"role": "assistant", "content": answer}


def process_message(message: str, history: list[dict] | None, responder: Callable):
    """Process a complete chat turn for callers that need both steps together."""
    messages, question = _append_question(message, history)
    if question:
        messages.append(_answer_message(question, messages[:-1], responder))
    return messages, ""


def reset_conversation():
    return [{"role": "assistant", "content": WELCOME_MESSAGE}], ""


def get_logo_data_url() -> str:
    image_data = (ASSETS / "finwiseiq-logo.png").read_bytes()
    return "data:image/png;base64," + base64.b64encode(image_data).decode("ascii")


def build_app(responder: Callable | None = None) -> gr.Blocks:
    """Create full interface. Inject a test responder for offline UI checks."""
    backend = responder if responder is not None else _real_responder()
    logo = get_logo_data_url()

    with gr.Blocks(
        title="FinWiseIQ | Islamic Finance & Compliance",
        fill_width=True,
    ) as demo:
        gr.HTML(
            f'''<header class="fw-nav" aria-label="FinWiseIQ brand header">
                <div class="fw-brand">
                    <img src="{logo}" alt="FinWiseIQ original logo" />
                    <div><strong>FinWiseIQ</strong><small>FINANCE • CLARITY • CONFIDENCE</small></div>
                </div>
                <div class="fw-live"><span class="fw-dot" aria-hidden="true"></span>Knowledge-powered assistant</div>
            </header>''',
            elem_id="fw-topline",
            container=False,
        )
        gr.HTML(
            '''<section class="fw-hero" aria-labelledby="fw-hero-title">
                <div class="fw-eyebrow">✦ ISLAMIC FINANCE • MALAYSIAN COMPLIANCE</div>
                <h1 id="fw-hero-title">Finance answers,<br/><em>made clearer.</em></h1>
                <p>Explore Islamic financing principles, Shariah-compliant banking,
                   AML/CFT and Malaysian financial regulations using FinWiseIQ's curated knowledge base.</p>
                <div class="fw-tags">
                    <span>✦ Islamic Finance</span><span>◇ KYC &amp; AML/CFT</span>
                    <span>◎ Malaysian Regulation</span>
                </div>
            </section>''',
            elem_id="fw-intro",
            container=False,
        )
        with gr.Column(elem_id="fw-chat-shell"):
            gr.HTML(
                '''<div class="fw-section-caption"><h2>✦ Ask FinWiseIQ</h2>
                <small>Explore • Ask • Learn</small></div>''',
                container=False,
            )
            transcript = gr.Chatbot(
                value=reset_conversation()[0],
                show_label=False,
                height=365,
                elem_id="fw-chatbox",
                buttons=["copy"],
            )
            with gr.Row(equal_height=True, elem_id="fw-composer"):
                query = gr.Textbox(
                    label="Your question",
                    placeholder="Ask about Islamic finance or Malaysian financial compliance...",
                    lines=1,
                    max_lines=3,
                    scale=8,
                    container=False,
                    html_attributes=gr.InputHTMLAttributes(enterkeyhint="send"),
                    elem_id="fw-question",
                )
                send = gr.Button("Send ↗", variant="primary", scale=1, min_width=95, elem_id="fw-send")
                clear = gr.Button("Clear", variant="secondary", scale=1, min_width=90, elem_id="fw-clear")

            gr.HTML('<div class="fw-suggest-text">TRY A SUGGESTED QUESTION</div>', elem_id="fw-suggestions-label", container=False)
            suggestions = {}
            with gr.Row(elem_classes="fw-suggestions"):
                for i, suggestion in enumerate(SUGGESTIONS):
                    chip = gr.Button(suggestion, variant="secondary", size="sm", key=f"fw-chip-{i}")
                    suggestions[chip] = suggestion

            pending_reply = gr.State({})

            async def show_question(message, history, pending, event: gr.EventData):
                if pending:
                    return gr.skip(), gr.skip()
                prompt = suggestions.get(event.target, message)
                messages, question = _append_question(prompt, history)
                if question:
                    pending["turn"] = (question, messages)
                    return messages + [{"role": "assistant", "content": LOADING_MESSAGE}], ""
                return messages, ""

            async def show_answer(pending):
                turn = pending.get("turn")
                if turn is None or pending.get("started"):
                    return gr.skip()
                pending["started"] = True
                try:
                    question, messages = turn
                    history = messages[:-1]
                    if history and _assistant_says(history[0], WELCOME_MESSAGE):
                        history = history[1:]
                    reply = await asyncio.to_thread(_answer_message, question, history, backend)
                    # Clear can remove this turn while the backend is still running.
                    return messages + [reply] if pending.get("turn") is turn else gr.skip()
                finally:
                    if pending.get("turn") is turn:
                        pending.clear()

            async def clear_chat(pending):
                pending.clear()
                return reset_conversation()

            submit = gr.on(
                [query.submit, send.click, *(chip.click for chip in suggestions)],
                fn=show_question,
                inputs=[query, transcript, pending_reply],
                outputs=[transcript, query],
                queue=False,
                show_progress="hidden",
            )
            answer = submit.then(
                fn=show_answer,
                inputs=pending_reply,
                outputs=transcript,
                show_progress="hidden",
            )
            clear.click(
                fn=clear_chat,
                inputs=pending_reply,
                outputs=[transcript, query],
                cancels=[answer],
                queue=False,
            )

        gr.HTML(
            '''<footer class="fw-footer-text">
                <strong>Educational information only.</strong> FinWiseIQ does not provide personal financial,
                legal, regulatory or Shariah advice. Always consult a qualified professional for formal decisions.
            </footer>''',
            elem_id="fw-footer",
            container=False,
        )

    return demo


if __name__ == "__main__":
    build_app().launch(
        theme=gr.themes.Soft(primary_hue="teal", secondary_hue="cyan", neutral_hue="slate"),
        css=CSS_FILE.read_text(encoding="utf-8"),
        inbrowser=True,
        favicon_path=str(ASSETS / "finwiseiq-favicon.ico"),
        show_error=False,
    )
