from pytradfri.util import load_json, save_json, BitChoices
import shutil, tempfile
from os import path
import unittest
import json


class UtilTestsBitChoices(unittest.TestCase):
    def test_bitchoices(self):
        WEEKDAYS = BitChoices(
            (
                ('tue', 'Tuesday'),
            )
        )

        assert WEEKDAYS.get_selected_keys(1) == ['tue']

class UtilTestsJSON(unittest.TestCase):
        def setUp(self):
            self.test_dir = tempfile.mkdtemp()

        def tearDown(self):
            shutil.rmtree(self.test_dir)

        def test_json_save(self):
            FILENAME = path.join(self.test_dir, 'sample_psk_file.txt')
            conf = {'identity': 'pytradfri',
                    'key': '123abc'}

            written_file = save_json(FILENAME, conf)
            self.assertTrue(written_file)

        def test_json_load(self):
            f = open(path.join(self.test_dir, 'sample_psk_file2.txt'), 'w')
            config = {'identity': 'hashstring',
                      'key': 'secretkey'}
            data = json.dumps(config, sort_keys=True, indent=4)
            f.write(data)
            f.close()

            json_data = load_json(path.join(self.test_dir, 'sample_psk_file2.txt'))
            self.assertEqual(json_data, {'identity': 'hashstring', 'key': 'secretkey'})