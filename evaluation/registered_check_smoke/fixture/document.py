"""Controlled smoke implementation: archiving retains the editable flag."""
def archive(document):
    document['archived'] = True
    return document
