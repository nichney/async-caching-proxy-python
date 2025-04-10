import unittest
from unittest.mock import patch, mock_open
import os
import json

from caching_proxy.cache import load_cache, save_cache


class TestLoadCache(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"proxy1": "value1", "proxy2": "value2"}')
    @patch("json.load")
    def test_load_cache_success(self, mock_json_load, mock_file):
        mock_json_load.return_value = {"proxy1": "value1", "proxy2": "value2"}
        result = load_cache()
        mock_file.assert_called_once_with("proxy_cache", "r")
        mock_json_load.assert_called_once_with(mock_file.return_value)
        self.assertEqual(result, {"proxy1": "value1", "proxy2": "value2"})

    @patch("builtins.open", side_effect=OSError("File not found"))
    @patch("json.load")
    def test_load_cache_oserror(self, mock_json_load, mock_file):
        result = load_cache()
        mock_file.assert_called_once_with("proxy_cache", "r")
        mock_json_load.assert_not_called()
        self.assertEqual(result, {})

    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    @patch("json.load", side_effect=json.JSONDecodeError("Error", "doc", 1))
    def test_load_cache_jsondecodeerror(self, mock_json_load, mock_file):
        result = load_cache()
        mock_file.assert_called_once_with("proxy_cache", "r")
        mock_json_load.assert_called_once_with(mock_file.return_value)
        self.assertEqual(result, {})

    @patch("builtins.open", new_callable=mock_open, read_data='')
    @patch("json.load")
    def test_load_cache_empty_file(self, mock_json_load, mock_file):
        mock_json_load.return_value = {}
        result = load_cache()
        mock_file.assert_called_once_with("proxy_cache", "r")
        mock_json_load.assert_called_once_with(mock_file.return_value)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
