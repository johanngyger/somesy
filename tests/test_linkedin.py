import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
import responses

import linkedin


from typing import Any, Dict, Generator, List


@pytest.fixture
def mock_env_vars() -> Generator[None, None, None]:
    with patch.dict(os.environ, {"LINKEDIN_TOKEN": "fake-token", "LINKEDIN_ORG_ID": "12345"}):
        yield


@pytest.fixture
def mock_linkedin_response() -> Dict[str, List[Dict[str, Any]]]:
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


def test_age_in_hours() -> None:
    # Test with a post from 5 hours ago
    now = datetime.now()
    post_time = int((now - timedelta(hours=5)).timestamp() * 1000)
    post = {"createdAt": post_time}

    age = linkedin.age_in_hours(post)

    # Allow some wiggle room for test execution time
    assert 4.9 < age < 5.1


def test_timestamp_from_activity_id() -> None:
    # Test extracting timestamp from a known activity ID
    # Activity ID 7413922466504495104 was posted around Dec 31, 2025
    timestamp_ms = linkedin.timestamp_from_activity_id("7413922466504495104")
    # Should be a valid timestamp in milliseconds (around late 2025)
    assert 1760000000000 < timestamp_ms < 1780000000000


def test_age_in_hours_from_activity_id() -> None:
    # Create an activity ID for "now" by reversing the Snowflake encoding
    now_ms = int(datetime.now().timestamp() * 1000)
    # LinkedIn IDs are ~63 bits, timestamp is in the first 41 bits
    # Left-shift by 22 to place timestamp in correct position
    fake_id = str(now_ms << 22)
    age = linkedin.age_in_hours_from_activity_id(fake_id)
    # Should be very close to 0 hours
    assert -0.1 < age < 0.1


def test_is_in_main_feed() -> None:
    assert linkedin.is_in_main_feed({"distribution": {"feedDistribution": "MAIN_FEED"}}) is True
    assert linkedin.is_in_main_feed({"distribution": {"feedDistribution": "NONE"}}) is False


@responses.activate
def test_recent_official_api_posts(
    mock_env_vars: None, mock_linkedin_response: Dict[str, List[Dict[str, Any]]]
) -> None:
    # Setup mock response
    responses.add(
        responses.GET,
        "https://api.linkedin.com/rest/posts?author=urn%3Ali%3Aorganization%3A12345&q=author&count=10&sortBy=CREATED",
        json=mock_linkedin_response,
        status=200,
    )

    # Call the function with 24 hour window
    posts = linkedin.recent_official_api_posts(24)

    # Should only return the first post (recent and in main feed)
    assert len(posts) == 1
    assert posts[0]["id"] == "post-1"


@responses.activate
def test_linkedin_api_error(mock_env_vars: None) -> None:
    # Mock a failed API response
    responses.add(
        responses.GET,
        "https://api.linkedin.com/rest/posts?author=urn%3Ali%3Aorganization%3A12345&q=author&count=10&sortBy=CREATED",
        json={"message": "API error"},
        status=401,
    )

    # Should raise an exception
    with pytest.raises(Exception) as e:
        linkedin.recent_official_api_posts()

    assert "LinkedIn Official API request failed with status 401" in str(e.value)


def test_recent_voyager_posts_no_credentials() -> None:
    # Without credentials, should return empty list
    result = linkedin.recent_voyager_posts(24)
    assert result == []


@pytest.fixture
def mock_voyager_env_vars() -> Generator[None, None, None]:
    with patch.dict(
        os.environ,
        {
            "LINKEDIN_LI_AT": "fake-li-at",
            "LINKEDIN_CSRF_TOKEN": "fake-csrf",
            "LINKEDIN_ORG_ID": "12345",
        },
    ):
        yield


@pytest.fixture
def mock_voyager_response() -> Dict[str, Any]:
    # Generate Snowflake-like IDs with embedded timestamps
    now_ms = int(datetime.now().timestamp() * 1000)
    id_1h_ago = str((now_ms - 1 * 3600 * 1000) << 22)  # 1 hour ago
    id_2d_ago = str((now_ms - 48 * 3600 * 1000) << 22)  # 48 hours ago
    id_1w_ago = str((now_ms - 168 * 3600 * 1000) << 22)  # 1 week ago
    return {
        "included": [
            {
                "entityUrn": f"urn:li:fsd_update:(urn:li:activity:{id_1h_ago},COMPANY_FEED_ADMIN,EMPTY,DEFAULT,false)",
            },
            {
                "entityUrn": f"urn:li:fsd_update:(urn:li:activity:{id_2d_ago},COMPANY_FEED_ADMIN,EMPTY,DEFAULT,false)",
            },
            {
                "entityUrn": f"urn:li:fsd_update:(urn:li:activity:{id_1w_ago},COMPANY_FEED_ADMIN,EMPTY,DEFAULT,false)",
            },
        ],
        "_test_ids": {"1h": id_1h_ago, "2d": id_2d_ago, "1w": id_1w_ago},
    }


@responses.activate
def test_recent_voyager_posts(
    mock_voyager_env_vars: None, mock_voyager_response: Dict[str, Any]
) -> None:
    # Setup mock response
    responses.add(
        responses.GET,
        "https://www.linkedin.com/voyager/api/graphql",
        json=mock_voyager_response,
        status=200,
    )

    # Call with 49 hour window (to include the 48h post)
    posts = linkedin.recent_voyager_posts(49)

    # Should return posts within 49h (1h and 48h), sorted oldest first (numerically)
    test_ids = mock_voyager_response["_test_ids"]
    assert len(posts) == 2
    assert posts == sorted([test_ids["1h"], test_ids["2d"]], key=int)


@responses.activate
def test_recent_voyager_posts_sorted_oldest_first(mock_voyager_env_vars: None) -> None:
    """Verify posts are sorted by ID ascending (oldest first).

    Snowflake IDs encode timestamp in the high bits, so numeric sorting
    by ID is equivalent to sorting by creation time.
    """
    # Generate realistic Snowflake IDs with embedded timestamps
    now_ms = int(datetime.now().timestamp() * 1000)
    id_1h_ago = str((now_ms - 1 * 3600 * 1000) << 22)
    id_3h_ago = str((now_ms - 3 * 3600 * 1000) << 22)
    id_5h_ago = str((now_ms - 5 * 3600 * 1000) << 22)

    # Return IDs in random order from API
    response = {
        "included": [
            {
                "entityUrn": f"urn:li:fsd_update:(urn:li:activity:{id_1h_ago},COMPANY_FEED_ADMIN,EMPTY,DEFAULT,false)"
            },
            {
                "entityUrn": f"urn:li:fsd_update:(urn:li:activity:{id_5h_ago},COMPANY_FEED_ADMIN,EMPTY,DEFAULT,false)"
            },
            {
                "entityUrn": f"urn:li:fsd_update:(urn:li:activity:{id_3h_ago},COMPANY_FEED_ADMIN,EMPTY,DEFAULT,false)"
            },
        ],
    }

    responses.add(
        responses.GET,
        "https://www.linkedin.com/voyager/api/graphql",
        json=response,
        status=200,
    )

    posts = linkedin.recent_voyager_posts(max_age_in_hours=24)

    # Should be sorted oldest first: 5h ago, 3h ago, 1h ago
    assert posts == [id_5h_ago, id_3h_ago, id_1h_ago]


@responses.activate
def test_recent_voyager_posts_api_error(mock_voyager_env_vars: None) -> None:
    # Mock a failed API response
    responses.add(
        responses.GET,
        "https://www.linkedin.com/voyager/api/graphql",
        json={"error": "Unauthorized"},
        status=401,
    )

    # Should raise an exception on API error with troubleshooting hint
    with pytest.raises(Exception) as e:
        linkedin.recent_voyager_posts(24)

    assert "Voyager API request failed with status 401" in str(e.value)
    assert "See README.md for troubleshooting" in str(e.value)


def test_recent_post_urls_uses_voyager() -> None:
    # When Voyager returns posts, use them
    with patch("linkedin.recent_voyager_posts", return_value=["111111", "222222"]):
        with patch("linkedin.recent_official_api_posts") as mock_official:
            urls = linkedin.recent_post_urls(24)

            assert urls == [
                "https://www.linkedin.com/feed/update/urn:li:activity:111111",
                "https://www.linkedin.com/feed/update/urn:li:activity:222222",
            ]
            mock_official.assert_not_called()


def test_recent_post_urls_falls_back_to_official() -> None:
    # When Voyager returns empty, fall back to official API
    with patch("linkedin.recent_voyager_posts", return_value=[]):
        with patch(
            "linkedin.recent_official_api_posts",
            return_value=[{"id": "urn:li:share:333333"}],
        ) as mock_official:
            urls = linkedin.recent_post_urls(48)

            assert urls == ["https://www.linkedin.com/feed/update/urn:li:share:333333"]
            mock_official.assert_called_once_with(48)
