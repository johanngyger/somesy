import linkedin
import slackc


def linkedin_to_slack(max_age=24):
    posts = linkedin.recent_linkedin_posts(max_age)
    messages = slackc.messages()
    for post in posts:
        msg = f"https://www.linkedin.com/feed/update/{post['id']}"
        if len([m for m in messages if msg in m['text']]) == 0:
            slackc.post_message(msg)
