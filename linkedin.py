import os
from datetime import datetime

import requests


def age_in_hours(post):
    created = datetime.fromtimestamp(post['createdAt'] / 1000.0)
    age = (datetime.now() - created).total_seconds() / 3600
    return age


def recent_linkedin_posts(max_age=24):
    linkedin_token = os.getenv('LINKEDIN_TOKEN')
    headers = {
        'Authorization': f'Bearer {linkedin_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202405'
    }
    # https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2024-05&tabs=http#find-posts-by-authors
    response = requests.get(
        'https://api.linkedin.com/rest/posts?author=urn%3Ali%3Aorganization%3A37403445&q=author&count=10&sortBy=CREATED',
        headers=headers)
    print(f'LinkedIn response: {response} {response.text}')
    posts = response.json()['elements']
    return [post for post in posts if age_in_hours(post) < max_age]
