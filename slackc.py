import os

from slack_sdk import WebClient


def slack_channel_id():
    return os.getenv('SLACK_CHANNEL_ID') or ''


def client():
    slack_token = os.getenv('SLACK_TOKEN')
    return WebClient(token=slack_token)


def messages():
    # find existing messages in channel
    # https://api.slack.com/methods/conversations.history
    response = client().conversations_history(channel=slack_channel_id())
    print(f'Slack response: {response}')
    messages = response["messages"]
    return messages


def post_message(message):
    client().chat_postMessage(channel=slack_channel_id(), text=message)
