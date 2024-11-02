import os

from slack_sdk import WebClient


def client():
    slack_token = os.getenv('SLACK_TOKEN')
    return WebClient(token=slack_token)


def messages():
    # find existing messages in channel
    # https://api.slack.com/methods/conversations.history
    response = client().conversations_history(channel='C020U24J998')
    print(f'Slack response: {response}')
    messages = response["messages"]
    return messages


def post_message(message):
    client().chat_postMessage(
        channel='#social-media',
        text=message
    )
