"""Test Util."""
import json
from os import path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pytest

from pytradfri.error import PytradfriError
from pytradfri.util import BitChoices, load_json, save_json


class UtilTestsBitChoices(unittest.TestCase):
    """Utility bit choices."""

    def test_bitchoices(self):
        """Test bit choices."""
        weekdays = BitChoices((("tue", "Tuesday"),))

        assert weekdays.get_selected_keys(1) == ["tue"]
        assert len(weekdays) == 1
        assert list(weekdays) == [(1, "Tuesday")]


class UtilTestsJSON(unittest.TestCase):
    """Utility JSON."""

    def setUp(self):
        """Create test suite."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Teardown test suite."""
        shutil.rmtree(self.test_dir)

    def test_json_save(self):
        """Test json save."""
        filename = path.join(self.test_dir, "sample_psk_file.txt")
        conf = {"identity": "pytradfri", "key": "123abc"}

        written_file = save_json(filename, conf)
        self.assertTrue(written_file)

    def test_json_load(self):
        """Test json load."""
        config = {"identity": "hashstring", "key": "secretkey"}
        data = json.dumps(config, sort_keys=True, indent=4)
        with open(
            path.join(self.test_dir, "sample_psk_file2.txt"), "w", encoding="utf-8"
        ) as fil:
            fil.write(data)

        json_data = load_json(path.join(self.test_dir, "sample_psk_file2.txt"))
        self.assertEqual(json_data, {"identity": "hashstring", "key": "secretkey"})

    def test_load_file_not_found(self):
        """Test json file missing."""
        assert not load_json(path.join(self.test_dir, "not_a_file"))

    def test_load_not_json(self):
        """Test of load not json."""
        data = "{not valid json"
        with open(
            path.join(self.test_dir, "sample_psk_file3.txt"), "w", encoding="utf-8"
        ) as fil:
            fil.write(data)

        with pytest.raises(PytradfriError):
            load_json(path.join(self.test_dir, "sample_psk_file3.txt"))

    def test_save_not_serializable(self):
        """Test save of illegal path."""
        filename = path.join(self.test_dir, "should_not_save")
        conf = b"bytes are not serializable"
        with pytest.raises(PytradfriError):
            save_json(filename, conf)

    def test_os_error(self):
        """Test os error is thrown."""
        with patch("builtins.open", side_effect=OSError(-1)):
            with pytest.raises(PytradfriError):
                load_json("whatever")
            with pytest.raises(PytradfriError):
                save_json("whatever", {})
