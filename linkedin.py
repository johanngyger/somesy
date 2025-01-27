import os
import urllib.parse
from datetime import datetime

import requests


def age_in_hours(post) -> float:
    created: datetime = datetime.fromtimestamp(post['createdAt'] / 1000.0)
    age: float = (datetime.now() - created).total_seconds() / 3600
    return age

def is_in_main_feed(post) -> bool:
    return post['distribution']['feedDistribution'] == 'MAIN_FEED'

def recent_linkedin_posts(max_age_in_hours: int = 24) -> list[dict[str, str]]:
    linkedin_token = os.getenv('LINKEDIN_TOKEN')
    headers: dict[str, str] = {
        'Authorization': f'Bearer {linkedin_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202405'
    }
    # https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/urns
    # urn:{namespace}:{entityType}:{id}, where: entityType is 'organization' or 'person'
    author_urn_url_enc: str = urllib.parse.quote_plus(os.getenv('LINKEDIN_AUTHOR') or '')
    # https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2024-10&tabs=http#find-posts-by-authors
    response = requests.get(
        f'https://api.linkedin.com/rest/posts?author={author_urn_url_enc}&q=author&count=10&sortBy=CREATED',
        headers=headers)
    if response.status_code != 200:
        raise Exception(f'LinkedIn API request failed with status {response.status_code}: {response.text}')
    posts: list[dict[str, str]] = response.json()['elements']
    recent_posts: list[dict[str, str]] = [post for post in posts if is_in_main_feed(post) and age_in_hours(post) < max_age_in_hours]
    print(f'Recent LinkedIn posts: {recent_posts}')
    return recent_posts
