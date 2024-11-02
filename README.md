# somesy – social media sync

![somesy](logo/somesy_200px.jpg)

A serverless Google Cloud Run function that syncs LinkedIn organization posts to a Slack channel.

## Configuration

The following environment variables are required:

- `LINKEDIN_TOKEN`: LinkedIn API token. See the section below how to get one
- `LINKEDIN_AUTHOR`: LinkedIn organization or person URN to read posts from
- `SLACK_TOKEN`: Slack bot user OAuth token
- `SLACK_CHANNEL_ID`: Slack channel ID to post messages to

### LinkedIn

Check [this article](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access) for details about
getting API access to LinkedIn.

*NOTE*: If you want to read posts from an organization, you need
to [apply](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access#marketing) for it.

1. Go to <https://www.linkedin.com/developers/tools/oauth>
2. Select the app you want to use
3. Select scope `r_organization_social` for organizations and `r_member_social` for individuals
4. Generate a token

### Slack

Create a Slack app: <https://api.slack.com/apps>.

Under OAuth & Permissions, set the following Bot Token Scopes: `channels:history` (public and private), `channels:read`, `chat:write`. 

## Google Cloud Run

### Deploying the function

```sh
gcloud functions deploy somesy --gen2 --runtime=python312 --region=europe-west6 --source=. --trigger-topic=somesy
```

## Local development and testing

### Configure test environment

Create a `.env` file in the root of the project with the environment variables mentioned above:

```text
LINKEDIN_TOKEN=...
SLACK_TOKEN=...
...
```

Install the required packages and run the function locally:

```
pip install -r requirements-test.txt
python main_test.py
```
