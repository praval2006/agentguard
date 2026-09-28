from contextlib import contextmanager
from app import Practice
from evaluation.set2.http_server import serve

@contextmanager
def application_server():
    with serve(Practice().dispatch) as base_url:
        yield base_url
