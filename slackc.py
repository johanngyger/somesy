import os
from typing import Any

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse


def slack_channel_id():
    return os.getenv('SLACK_CHANNEL_ID', '')


def slack_client() -> WebClient:
    slack_token = os.getenv('SLACK_TOKEN', '')
    return WebClient(token=slack_token)


def slack_messages() -> list[dict[str, Any]]:
    # find existing messages in channel
    # https://api.slack.com/methods/conversations.history
    channel_id = slack_channel_id()
    response: SlackResponse = slack_client().conversations_history(channel=channel_id)
    print(f'Slack messages from channel {channel_id}: {response}')
    messages: list[dict[str, Any]] = response["messages"]
    return messages


def post_slack_message(message: str) -> None:
    channel_id = slack_channel_id()
    print(f'Posting Slack message to channel {channel_id}: {message}')
    slack_client().chat_postMessage(channel=slack_channel_id(), text=message)
