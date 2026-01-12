import os
import re
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List

import requests


def age_in_hours(post: Dict[str, Any]) -> float:
    created: datetime = datetime.fromtimestamp(post["createdAt"] / 1000.0)
    age: float = (datetime.now() - created).total_seconds() / 3600
    return age


def is_in_main_feed(post: Dict[str, Any]) -> bool:
    return str(post["distribution"]["feedDistribution"]) == "MAIN_FEED"


def timestamp_from_activity_id(activity_id: str) -> int:
    """Extract Unix timestamp (milliseconds) from LinkedIn activity ID.

    LinkedIn uses Snowflake IDs where the first 41 bits contain the timestamp.
    """
    as_binary = bin(int(activity_id))[2:]  # Remove '0b' prefix, no zero-padding
    timestamp_bits = as_binary[:41]
    return int(timestamp_bits, 2)


def age_in_hours_from_activity_id(activity_id: str) -> float:
    """Calculate age in hours from LinkedIn activity ID."""
    created_ms = timestamp_from_activity_id(activity_id)
    now_ms = datetime.now().timestamp() * 1000
    return (now_ms - created_ms) / (1000 * 3600)


def recent_voyager_posts(max_age_in_hours: int = 24) -> List[str]:
    """Fetch recent posts using LinkedIn's internal Voyager API.

    This fetches posts from the admin page, including those created via
    LinkedIn's native scheduler (which the official Posts API doesn't return).

    Returns a list of activity IDs (just the numeric part).
    Raises an exception if the API call fails.
    """
    li_at = os.getenv("LINKEDIN_LI_AT")
    csrf_token = os.getenv("LINKEDIN_CSRF_TOKEN")
    org_id = os.getenv("LINKEDIN_ORG_ID")

    if not all([li_at, csrf_token, org_id]):
        print("LinkedIn Voyager API: credentials not configured, skipping")
        return []

    # Type narrowing for mypy after the None check above
    assert li_at is not None and csrf_token is not None

    headers: Dict[str, str] = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": csrf_token,
        "x-restli-protocol-version": "2.0.0",
    }
    cookies: Dict[str, str] = {
        "li_at": li_at,
        "JSESSIONID": f'"{csrf_token}"',
    }

    variables = (
        f"(organizationalPageFeedUseCase:ADMIN_ORGANIZATIONAL_PAGE_POSTS,"
        f"organizationalPageIdOrUniversalName:(organizationalPageUUId:{org_id}),"
        f"start:0,count:10,numComments:0)"
    )
    query_id = "voyagerFeedDashOrganizationalPageAdminUpdates.674de8f5f692ab9c9ce0ab819ecae05e"

    response = requests.get(
        f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables={variables}&queryId={query_id}",
        headers=headers,
        cookies=cookies,
    )

    if response.status_code != 200:
        raise Exception(
            f"Voyager API request failed with status {response.status_code}: {response.text}. "
            f"See README.md for troubleshooting (expired cookies, outdated queryId, etc.)"
        )

    data = response.json()

    # Extract activity IDs from fsd_update items
    included = data.get("included", [])
    activity_ids: List[str] = []

    for item in included:
        entity_urn = item.get("entityUrn", "")
        if "fsd_update:(urn:li:activity:" in entity_urn:
            match = re.search(r"urn:li:activity:(\d+)", entity_urn)
            if match:
                activity_ids.append(match.group(1))

    # Filter by max age using timestamp from Snowflake ID
    filtered_ids = [
        aid for aid in activity_ids if age_in_hours_from_activity_id(aid) <= max_age_in_hours
    ]

    # Sort by ID ascending (oldest first, so newest appears last in Slack), limit to 10
    sorted_ids = sorted(filtered_ids, key=int)[:10]
    print(f"LinkedIn Voyager API: {len(sorted_ids)} posts within {max_age_in_hours}h:")
    for aid in sorted_ids:
        age = age_in_hours_from_activity_id(aid)
        print(f"  urn:li:activity:{aid} ({age:.1f}h ago)")
    return sorted_ids


def recent_official_api_posts(max_age_in_hours: int = 24) -> List[Dict[str, Any]]:
    """Fetch recent posts using LinkedIn's official Posts API.

    Note: This API does not return posts created via LinkedIn's native scheduler.
    Use recent_voyager_posts() for those.

    Returns a list of post objects with 'id' field containing the URN.
    """
    linkedin_token = os.getenv("LINKEDIN_TOKEN")
    org_id = os.getenv("LINKEDIN_ORG_ID")
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {linkedin_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202505",
    }
    # https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/urns
    author_urn_url_enc: str = urllib.parse.quote_plus(f"urn:li:organization:{org_id}")
    # https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2024-10&tabs=http#find-posts-by-authors
    response = requests.get(
        f"https://api.linkedin.com/rest/posts?author={author_urn_url_enc}&q=author&count=10&sortBy=CREATED",
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"LinkedIn Official API request failed with status {response.status_code}: {response.text}"
        )
    posts: List[Dict[str, Any]] = response.json()["elements"]
    recent_posts: List[Dict[str, Any]] = [
        post for post in posts if is_in_main_feed(post) and age_in_hours(post) <= max_age_in_hours
    ]
    print(f"LinkedIn Official API: {len(recent_posts)} posts within {max_age_in_hours}h:")
    for post in recent_posts:
        print(f"  {post['id']} ({age_in_hours(post):.1f}h ago)")
    return recent_posts


def recent_post_urls(max_age_in_hours: int = 24) -> List[str]:
    """Get recent LinkedIn post URLs.

    Tries the Voyager API first (includes natively scheduled posts),
    falls back to the official Posts API if Voyager returns no posts.

    Returns a list of LinkedIn post URLs, oldest first.
    """
    activity_ids = recent_voyager_posts(max_age_in_hours)

    if activity_ids:
        return [
            f"https://www.linkedin.com/feed/update/urn:li:activity:{aid}" for aid in activity_ids
        ]

    # Fall back to official Posts API
    posts = recent_official_api_posts(max_age_in_hours)
    return [f"https://www.linkedin.com/feed/update/{post['id']}" for post in posts]
