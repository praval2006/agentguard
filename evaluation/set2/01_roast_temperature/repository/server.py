from contextlib import contextmanager
from app import dispatch
from evaluation.set2.http_server import serve

@contextmanager
def application_server():
    with serve(dispatch) as base_url:
        yield base_url
