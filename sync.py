import linkedin
import slackc
from typing import Any, Dict, List


def linkedin_to_slack(max_age_in_hours: int = 24) -> None:
    posts: List[Dict[str, Any]] = linkedin.recent_linkedin_posts(max_age_in_hours)
    messages: List[Dict[str, Any]] = slackc.slack_messages()
    for post in posts:
        msg = f"https://www.linkedin.com/feed/update/{post['id']}"
        if len([m for m in messages if msg in m["text"]]) == 0:
            slackc.post_slack_message(msg)
