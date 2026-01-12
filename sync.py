import linkedin
import slackc


def linkedin_to_slack(max_age_in_hours: int = 24) -> None:
    """Sync LinkedIn posts to Slack."""
    slack_texts = [m.get("text", "") for m in slackc.slack_messages()]
    post_urls = linkedin.recent_post_urls(max_age_in_hours)

    for url in post_urls:
        if not any(url in text for text in slack_texts):
            slackc.post_slack_message(url)
