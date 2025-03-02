import os
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk import WebClient

import slackc


@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        "SLACK_TOKEN": "fake-slack-token",
        "SLACK_CHANNEL_ID": "C12345678"
    }):
        yield


def test_slack_channel_id():
    with patch.dict(os.environ, {"SLACK_CHANNEL_ID": "test-channel"}):
        assert slackc.slack_channel_id() == "test-channel"
    
    # Test default value
    with patch.dict(os.environ, {}, clear=True):
        assert slackc.slack_channel_id() == ""


def test_slack_client():
    with patch.dict(os.environ, {"SLACK_TOKEN": "test-token"}):
        client = slackc.slack_client()
        assert isinstance(client, WebClient)
        assert client.token == "test-token"


@pytest.fixture
def mock_slack_response():
    return {
        "ok": True,
        "messages": [
            {"type": "message", "text": "https://www.linkedin.com/feed/update/existing-post"},
            {"type": "message", "text": "Just a regular message"}
        ]
    }


def test_slack_messages(mock_env_vars):
    with patch.object(slackc, "slack_client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        mock_instance.conversations_history.return_value = {
            "ok": True,
            "messages": [
                {"text": "Message 1"},
                {"text": "Message 2"}
            ]
        }
        
        messages = slackc.slack_messages()
        
        # Verify correct parameters
        mock_instance.conversations_history.assert_called_once_with(channel="C12345678")
        assert len(messages) == 2
        assert messages[0]["text"] == "Message 1"


def test_post_slack_message(mock_env_vars):
    with patch.object(slackc, "slack_client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        slackc.post_slack_message("Test message")
        
        # Verify correct parameters
        mock_instance.chat_postMessage.assert_called_once_with(
            channel="C12345678", 
            text="Test message"
        )
