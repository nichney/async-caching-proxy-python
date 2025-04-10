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


class TestSaveCache(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_cache_success(self, mock_json_dump, mock_file):
        cache_data = {"proxy3": "value3", "proxy4": "value4"}
        save_cache(cache_data)
        mock_file.assert_called_once_with("proxy_cache", "w")
        mock_json_dump.assert_called_once_with(cache_data, mock_file.return_value)

    @patch("builtins.open", side_effect=OSError("Permission denied"))
    @patch("json.dump")
    def test_save_cache_oserror(self, mock_json_dump, mock_file):
        cache_data = {"proxy5": "value5"}
        with self.assertRaises(OSError) as context:
            save_cache(cache_data)
        mock_file.assert_called_once_with("proxy_cache", "w")
        mock_json_dump.assert_not_called()
        self.assertEqual(str(context.exception), "Permission denied")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump", side_effect=TypeError("Object of type set is not JSON serializable"))
    def test_save_cache_typeerror(self, mock_json_dump, mock_file):
        cache_data = {"proxy6": {1, 2, 3}}  # Non-serializable data
        with self.assertRaises(TypeError) as context:
            save_cache(cache_data)
        mock_file.assert_called_once_with("proxy_cache", "w")
        mock_json_dump.assert_called_once_with(cache_data, mock_file.return_value)
        self.assertEqual(str(context.exception), "Object of type set is not JSON serializable")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_cache_empty_cache(self, mock_json_dump, mock_file):
        cache_data = {}
        save_cache(cache_data)
        mock_file.assert_called_once_with("proxy_cache", "w")
        mock_json_dump.assert_called_once_with(cache_data, mock_file.return_value)

if __name__ == "__main__":
    unittest.main()
