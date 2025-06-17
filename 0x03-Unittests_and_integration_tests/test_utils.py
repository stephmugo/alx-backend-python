#!/usr/bin/env python3
"""Unit tests for utils.py functions."""

import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function."""

    @parameterized.expand([
        # Test cases: (input_dict, path_tuple, expected_result)
        ({"a": 1}, ("a",), 1),                          # Simple key access
        ({"a": {"b": 2}}, ("a",), {"b": 2}),           # Access nested dict
        ({"a": {"b": 2}}, ("a", "b"), 2),     # Access deeply nested value
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test normal access of nested maps with valid paths."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        # Test cases that should raise KeyError
        ({}, ("a",)),                   # Empty dict, non-existent key
        ({"a": {"b": 2}}, ("a", "c")),  # Valid first key, invalid second key
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test access_nested_map raises KeyError when path doesn't exist."""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        # Verify the exception message contains the last key in the path
        self.assertEqual(str(cm.exception), repr(path[-1]))


class TestGetJson(unittest.TestCase):
    """Test cases for the get_json function."""

    @parameterized.expand([
        # Test cases: (url, expected_json_payload)
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test get_json makes GET request & returns expected payload"""
        # Mock the requests.get function to avoid actual HTTP calls
        with patch('utils.requests.get') as mock_get:
            # Create a mock response object
            mock_response = Mock()
            mock_response.json.return_value = test_payload
            mock_get.return_value = mock_response

            # Call the function under test
            result = get_json(test_url)

            # Verify requests.get was called once with the correct URL
            mock_get.assert_called_once_with(test_url)
            # Verify the function returns the expected JSON payload
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for the memoize decorator."""

    def test_memoize(self):
        """Test memoization caches result & avoids repeated method calls"""

        class TestClass:
            def a_method(self):
                """Method that returns a value - will be mocked."""
                return 42

            @memoize
            def a_property(self):
                """Property that uses memoization to cache a_method result."""
                return self.a_method()

        # Mock a_method to track how many times it's called
        with patch.object(
            TestClass, "a_method", return_value=42
        ) as mocked_method:
            test_obj = TestClass()

            # Call the memoized property twice
            result1 = test_obj.a_property
            result2 = test_obj.a_property

            # Both calls should return the same value
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # underlying method should only be called once
            mocked_method.assert_called_once()


# Standard Python idiom to run tests when script is executed directly
if __name__ == "__main__":
    unittest.main()
