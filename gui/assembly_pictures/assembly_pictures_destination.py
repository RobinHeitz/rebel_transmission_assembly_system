import pathlib

def _get_img_dir() -> pathlib.Path:
    p = pathlib.Path(__file__).parent
    return p