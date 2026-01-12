from unittest.mock import patch

import pytest

import sync

from typing import Dict, List


@pytest.fixture
def mock_slack_messages() -> List[Dict[str, str]]:
    return [
        {"text": "https://www.linkedin.com/feed/update/urn:li:activity:111111"},
        {"text": "Just a regular message"},
    ]


def test_linkedin_to_slack_posts_new(mock_slack_messages: List[Dict[str, str]]) -> None:
    # Test posting new URLs that aren't in Slack yet
    with patch(
        "sync.linkedin.recent_post_urls",
        return_value=[
            "https://www.linkedin.com/feed/update/urn:li:activity:111111",
            "https://www.linkedin.com/feed/update/urn:li:activity:222222",
        ],
    ) as mock_linkedin:
        with patch(
            "sync.slackc.slack_messages", return_value=mock_slack_messages
        ) as mock_slack_get:
            with patch("sync.slackc.post_slack_message") as mock_slack_post:
                sync.linkedin_to_slack(24)

                mock_linkedin.assert_called_once_with(24)
                mock_slack_get.assert_called_once()

                # Should only post 222222, since 111111 is already in Slack
                assert mock_slack_post.call_count == 1
                mock_slack_post.assert_called_once_with(
                    "https://www.linkedin.com/feed/update/urn:li:activity:222222"
                )


def test_linkedin_to_slack_no_new_posts() -> None:
    # All posts already in Slack
    with patch(
        "sync.linkedin.recent_post_urls",
        return_value=["https://www.linkedin.com/feed/update/urn:li:activity:111111"],
    ):
        with patch(
            "sync.slackc.slack_messages",
            return_value=[{"text": "https://www.linkedin.com/feed/update/urn:li:activity:111111"}],
        ):
            with patch("sync.slackc.post_slack_message") as mock_slack_post:
                sync.linkedin_to_slack(24)
                mock_slack_post.assert_not_called()


def test_linkedin_to_slack_no_posts() -> None:
    # No LinkedIn posts at all
    with patch("sync.linkedin.recent_post_urls", return_value=[]):
        with patch("sync.slackc.slack_messages", return_value=[]):
            with patch("sync.slackc.post_slack_message") as mock_slack_post:
                sync.linkedin_to_slack(24)
                mock_slack_post.assert_not_called()
