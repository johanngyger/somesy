import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
import responses

import linkedin


@pytest.fixture
def mock_env_vars():
    with patch.dict(
        os.environ, {"LINKEDIN_TOKEN": "fake-token", "LINKEDIN_AUTHOR": "urn:li:organization:12345"}
    ):
        yield


@pytest.fixture
def mock_linkedin_response():
    post_time = int((datetime.now() - timedelta(hours=12)).timestamp() * 1000)
    return {
        "elements": [
            {
                "id": "post-1",
                "createdAt": post_time,
                "distribution": {"feedDistribution": "MAIN_FEED"},
            },
            {
                "id": "post-2",
                "createdAt": post_time - 1000 * 3600 * 48,  # 48 hours older
                "distribution": {"feedDistribution": "MAIN_FEED"},
            },
            {
                "id": "post-3",
                "createdAt": post_time,
                "distribution": {"feedDistribution": "NONE"},  # Not in main feed
            },
        ]
    }


def test_age_in_hours():
    # Test with a post from 5 hours ago
    now = datetime.now()
    post_time = int((now - timedelta(hours=5)).timestamp() * 1000)
    post = {"createdAt": post_time}

    age = linkedin.age_in_hours(post)

    # Allow some wiggle room for test execution time
    assert 4.9 < age < 5.1


def test_is_in_main_feed():
    assert linkedin.is_in_main_feed({"distribution": {"feedDistribution": "MAIN_FEED"}}) is True
    assert linkedin.is_in_main_feed({"distribution": {"feedDistribution": "NONE"}}) is False


@responses.activate
def test_recent_linkedin_posts(mock_env_vars, mock_linkedin_response):
    # Setup mock response
    responses.add(
        responses.GET,
        "https://api.linkedin.com/rest/posts?author=urn%3Ali%3Aorganization%3A12345&q=author&count=10&sortBy=CREATED",
        json=mock_linkedin_response,
        status=200,
    )

    # Call the function with 24 hour window
    posts = linkedin.recent_linkedin_posts(24)

    # Should only return the first post (recent and in main feed)
    assert len(posts) == 1
    assert posts[0]["id"] == "post-1"


@responses.activate
def test_linkedin_api_error(mock_env_vars):
    # Mock a failed API response
    responses.add(
        responses.GET,
        "https://api.linkedin.com/rest/posts?author=urn%3Ali%3Aorganization%3A12345&q=author&count=10&sortBy=CREATED",
        json={"message": "API error"},
        status=401,
    )

    # Should raise an exception
    with pytest.raises(Exception) as e:
        linkedin.recent_linkedin_posts()

    assert "LinkedIn API request failed with status 401" in str(e.value)
