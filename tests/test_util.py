from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json, BitChoices
import shutil
import tempfile
from os import path
import unittest
from unittest.mock import Mock, patch, mock_open
import json
import pytest


class UtilTestsBitChoices(unittest.TestCase):
    def test_bitchoices(self):
        WEEKDAYS = BitChoices(
            (
                ('tue', 'Tuesday'),
            )
        )

        assert WEEKDAYS.get_selected_keys(1) == ['tue']
        assert len(WEEKDAYS) == 1
        assert [x for x in WEEKDAYS] == [(1, 'Tuesday')]


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

            json_data = load_json(path.join(self.test_dir,
                                            'sample_psk_file2.txt'))
            self.assertEqual(json_data,
                             {'identity': 'hashstring', 'key': 'secretkey'})

        def test_load_file_not_found(self):
            assert not load_json(path.join(self.test_dir, 'not_a_file'))

        def test_load_not_json(self):
            f = open(path.join(self.test_dir, 'sample_psk_file3.txt'), 'w')
            data = '{not valid json'
            f.write(data)
            f.close()

            with pytest.raises(PytradfriError):
                load_json(path.join(self.test_dir, 'sample_psk_file3.txt'))

        def test_save_not_serializable(self):
            FILENAME = path.join(self.test_dir, 'should_not_save')
            conf = b'bytes are not serializable'
            with pytest.raises(PytradfriError):
                written_file = save_json(FILENAME, conf)

        def test_os_error(self):
            with patch("builtins.open", side_effect=OSError(-1)):
                 with pytest.raises(PytradfriError):
                     load_json('whatever')
                 with pytest.raises(PytradfriError):
                     save_json('whatever', {})

