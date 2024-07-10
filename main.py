import gradio as gr
from youtube import extract_text_from_video


def _wrapper(text: str):
    return extract_text_from_video(video_url=text)


demo = gr.Interface(
    fn=_wrapper,
    inputs=["text"],
    outputs=["text"],
)

demo.launch()
