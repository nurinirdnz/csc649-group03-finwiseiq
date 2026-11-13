
import gradio as gr


def respond(message, history):
    """Return a temporary response while the backend is being developed."""
    if not message.strip():
        return "Please type a question."

    return "This is a demo response. The FinWiseIQ backend will be connected soon."


demo = gr.ChatInterface(
    fn=respond,
    title="FinWiseIQ",
    description=(
        "An AI-powered Islamic Finance and Malaysian Financial "
        "Compliance Assistant.\n\n"
        "Educational information only. Not professional financial, "
        "legal, regulatory or Shariah advice."
    ),
)


if __name__ == "__main__":
    demo.launch()
