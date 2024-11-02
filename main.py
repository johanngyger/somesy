import base64
import functions_framework
import sync

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def somesy(cloud_event):
    sync.linkedin_to_slack(48)
