import os
import tempfile
from typing import List
import yt_dlp as youtube_dl
import webvtt

from diskcache import cache_decorator


def parse_vtt(file: str) -> str:
    """Youtube VTT parsing function. The VTT file have duplicated line and format in
    a weird way, so this will partially clean it up.

    Args:
        file (str): the path

    Returns:
        Cleaned transcript
    """
    lines = []
    for caption in webvtt.read(file):
        lines.extend(str(caption.text).strip().splitlines())
        pass

    lines = [line for line in lines if len(line) > 0]

    # Remove repeated lines
    previous = None
    transcript = ""
    for line in lines:
        if line == previous:
            continue
        transcript += " " + line
        previous = line

    return transcript


@cache_decorator
def extract_text_from_video(video_url: str) -> str | None:
    with youtube_dl.YoutubeDL({}) as ydl:
        info = ydl.extract_info(video_url, download=False)
        pass

    text = None
    with tempfile.TemporaryDirectory() as _tmp_dir_name:
        try:
            _ = info["automatic_captions"]["en-orig"]
            text = get_subtitles(video_url, _tmp_dir_name)
        except Exception as e:
            print(e)
            pass

    return text


def get_subtitles(video_url: str, output_dir: str = None) -> str | None:
    ydl_opts = {
        "writeautomaticsub": True,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en-orig"],
        "skip_download": True,
        "outtmpl": {
            "default": f"{output_dir}/" + "%(title)s.%(ext)s",
        },
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        pass

    _top_file = next(os.walk(output_dir))
    _top_file = os.path.join(_top_file[0], _top_file[2][0])
    if _top_file.endswith(".vtt"):
        return parse_vtt(_top_file)

    return None


if __name__ == "__main__":
    text = extract_text_from_video(
        video_url="https://www.youtube.com/watch?v=no7EQkOiHQM"
    )

    print(text)
    pass
