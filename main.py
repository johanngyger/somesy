import functions_framework
from cloudevents.http import CloudEvent

import sync


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def somesy(cloud_event: CloudEvent) -> None:
    sync.linkedin_to_slack(2 * 24)
