#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient class."""

import unittest
from unittest import TestCase
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient

# Inline fixtures here as ALX expects everything in one file
# Test data representing a GitHub organization's API response
org_payload = {
    "login": "google",
    "id": 1,
    "repos_url": "https://api.github.com/orgs/google/repos"
}

# Test data representing repositories returned by GitHub API
repos_payload = [
    {"name": "repo1", "license": {"key": "apache-2.0"}},
    {"name": "repo2", "license": {"key": "mit"}},
    {"name": "repo3", "license": {"key": "apache-2.0"}}
]

# Expected list of repository names extracted from repos_payload
expected_repos = ["repo1", "repo2", "repo3"]

# Expected repositories filtered by Apache 2.0 license
apache2_repos = ["repo1", "repo3"]


class TestGithubOrgClient(TestCase):
    """Unit tests for the GithubOrgClient class."""

    @parameterized.expand([
        # Test cases: (test_name, org_name, expected_api_response)
        ("case_google", "google", {"login": "google", "id": 1}),
        ("case_abc", "abc", {"login": "abc", "id": 2})
    ])
    
    @patch("client.get_json")  # Mock the get_json function to avoid real API calls
    def test_org(self, _, org_name, expected_response, mock_get_json):
        """Test that GithubOrgClient.org returns the expected org data."""
        # Configure the mock to return our test data
        mock_get_json.return_value = expected_response
        
        # Create client instance and call the method under test
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org(), expected_response)
        
        # Verify get_json was called with the correct GitHub API URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch("client.get_json")  # Mock get_json to control API response
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repo names."""
        # Mock the API response containing repository data
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]

        # Mock the _public_repos_url property to avoid dependency on org() method
        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            # Set the mocked property to return a test URL
            mock_url.return_value = "https://api.github.com/orgs/testorg/repos"
            
            # Create client and test the public_repos method
            client = GithubOrgClient("testorg")
            result = client.public_repos()
            
            # Verify the method returns only repository names
            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            # Verify get_json was called with the repos URL
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/testorg/repos"
            )
            # Verify the _public_repos_url property was accessed
            mock_url.assert_called_once()

    @parameterized.expand([
        (
            {"license": {"key": "my_license"}},  # repo data with license
            "my_license",                        # license_key to check
            True                                 # expected result (match)
        ),
        (
            {"license": {"key": "other_license"}},  # repo with different license
            "my_license",                           # license_key to check
            False                                   # expected result (no match)
        )
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license correctly detects license matches."""
        client = GithubOrgClient("testorg")
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class([{
    # Inject test data as class attributes for integration tests
    "org_payload": org_payload,
    "repos_payload": repos_payload, 
    "expected_repos": expected_repos,
    "apache2_repos": apache2_repos
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos with real HTTP mocking."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level mocks that persist across all test methods."""
        # Start patching requests.get at the module level for integration testing
        cls.get_patcher = patch('client.requests.get')
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Mock function that returns different responses based on URL."""
            mock_response = unittest.mock.Mock()
            # Mock the raise_for_status method (doesn't need to do anything)
            mock_response.raise_for_status = unittest.mock.Mock()

            # Return appropriate test data based on the requested URL
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                # Default response for any other URLs
                mock_response.json.return_value = {}
            return mock_response

        # Configure the mock to use our side_effect function
        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level mocks after all tests complete."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns expected repos in integration scenario."""
        client = GithubOrgClient("google")
        # Test the full flow: org() -> _public_repos_url -> public_repos()
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter returns correct repos."""
        client = GithubOrgClient("google")
        # Test license filtering functionality
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)


# Standard Python idiom to run tests when script is executed directly
if __name__ == "__main__":
    unittest.main()