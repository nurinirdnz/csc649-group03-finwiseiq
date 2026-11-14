import gradio as gr


def respond(message, history):
    """Return a temporary response while the backend is being developed."""
    if not message.strip():
        return "Please type a question."

    return "This is a demo response. The FinWiseIQ backend will be connected soon."


demo = gr.ChatInterface(
    fn=respond,
    title="FinWiseIQ",
    examples=[
        "What is Murabahah financing?",
        "What is Islamic banking?",
        "What is Shariah-compliant financing?",
        "What is the difference between zakat and tax?"
    ],
    textbox=gr.Textbox(
        placeholder="Ask a question about Islamic finance or Malaysian financial compliance...",
        lines=1,
        max_lines=3,
    ),
    description=(
        "An AI-powered Islamic Finance and Malaysian Financial "
        "Compliance Assistant.\n\n"
        "Educational information only. Not professional financial, "
        "legal, regulatory or Shariah advice."
    ),
)


if __name__ == "__main__":
    demo.launch()
