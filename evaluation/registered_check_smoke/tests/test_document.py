import unittest
from fixture.document import archive

class DocumentAcceptance(unittest.TestCase):
    def test_archive_flag(self):
        document = archive({'archived': False, 'editable': True})
        self.assertIs(document['archived'], True)

    def test_archive_disables_editing(self):
        document = archive({'archived': False, 'editable': True})
        self.assertIs(document['editable'], False)
