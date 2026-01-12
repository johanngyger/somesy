import os
import re
from typing import Any, Dict, List

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse


def slack_channel_id() -> str:
    return os.getenv("SLACK_CHANNEL_ID", "")


def slack_client() -> WebClient:
    slack_token = os.getenv("SLACK_TOKEN", "")
    return WebClient(token=slack_token)


def slack_messages() -> List[Dict[str, Any]]:
    # find existing messages in channel
    # https://api.slack.com/methods/conversations.history
    channel_id = slack_channel_id()
    response: SlackResponse = slack_client().conversations_history(channel=channel_id)
    messages: List[Dict[str, Any]] = response["messages"]
    # Extract URNs from message URLs for logging
    urns = []
    for m in messages:
        text = m.get("text", "")
        match = re.search(r"(urn:li:(?:activity|share|ugcPost):\d+)", text)
        if match:
            urns.append(match.group(1))
    # Sort by ID ascending (oldest first)
    sorted_urns = sorted(urns, key=lambda u: int(u.split(":")[-1]))
    print(f"Slack channel: {len(sorted_urns)} LinkedIn posts:")
    for urn in sorted_urns:
        print(f"  {urn}")
    return messages


def post_slack_message(message: str) -> None:
    print(f"Posting to Slack: {message}")
    slack_client().chat_postMessage(channel=slack_channel_id(), text=message)
