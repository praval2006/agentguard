from contextlib import contextmanager
from app import Application
from evaluation.set3.transport import serve

@contextmanager
def application_server(application=None):
    with serve(Application() if application is None else application) as base_url:
        yield base_url
