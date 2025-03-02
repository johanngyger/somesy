from unittest.mock import patch

import functions_framework

import main


def test_somesy_cloud_function() -> None:
    # Mock the sync module
    with patch("main.sync.linkedin_to_slack") as mock_sync:
        # Create a mock cloud event
        cloud_event = functions_framework.CloudEvent(
            attributes={
                "type": "google.cloud.pubsub.topic.v1.messagePublished",
                "source": "//pubsub.googleapis.com/projects/project-id/topics/somesy",
            },
            data={},
        )

        # Call the cloud function
        main.somesy(cloud_event)

        # Verify sync was called with the correct parameter
        mock_sync.assert_called_once_with(48)
