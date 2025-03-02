from unittest.mock import patch

import pytest

import sync


from typing import Dict, List


@pytest.fixture
def mock_linkedin_posts() -> List[Dict[str, str]]:
    return [{"id": "post-1"}, {"id": "post-2"}]


@pytest.fixture
def mock_slack_messages() -> List[Dict[str, str]]:
    return [
        {"text": "https://www.linkedin.com/feed/update/post-1"},
        {"text": "Just a regular message"},
    ]


def test_linkedin_to_slack_new_posts(
    mock_linkedin_posts: List[Dict[str, str]], mock_slack_messages: List[Dict[str, str]]
) -> None:
    # Mock the LinkedIn and Slack modules
    with patch(
        "sync.linkedin.recent_linkedin_posts", return_value=mock_linkedin_posts
    ) as mock_linkedin:
        with patch(
            "sync.slackc.slack_messages", return_value=mock_slack_messages
        ) as mock_slack_get:
            with patch("sync.slackc.post_slack_message") as mock_slack_post:
                # Run the function
                sync.linkedin_to_slack(24)

                # Verify expected calls
                mock_linkedin.assert_called_once_with(24)
                mock_slack_get.assert_called_once()

                # Should only post post-2, which isn't in the mock messages
                assert mock_slack_post.call_count == 1
                mock_slack_post.assert_called_once_with(
                    "https://www.linkedin.com/feed/update/post-2"
                )


def test_linkedin_to_slack_no_new_posts() -> None:
    # Mock the LinkedIn and Slack modules with no new posts
    with patch(
        "sync.linkedin.recent_linkedin_posts", return_value=[{"id": "post-1"}]
    ) as mock_linkedin:
        with patch(
            "sync.slackc.slack_messages",
            return_value=[{"text": "https://www.linkedin.com/feed/update/post-1"}],
        ) as mock_slack_get:
            with patch("sync.slackc.post_slack_message") as mock_slack_post:
                # Run the function
                sync.linkedin_to_slack(24)

                # Verify expected calls
                mock_linkedin.assert_called_once_with(24)
                mock_slack_get.assert_called_once()

                # Should not post anything as the post is already in Slack
                mock_slack_post.assert_not_called()
