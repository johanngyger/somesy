# somesy – social media sync

![somesy](logo/somesy_200px.jpg)

A serverless Google Cloud Run function that syncs LinkedIn posts to a Slack channel.

## Configuration

The following environment variables are required:

- `LINKEDIN_TOKEN`: LinkedIn OAuth token
- `LINKEDIN_ORG_ID`: Your LinkedIn organization's numeric ID
- `SLACK_TOKEN`: Slack bot user OAuth token
- `SLACK_CHANNEL_ID`: Slack channel ID to post messages to

### Optional: Voyager API (for scheduled posts)

Posts created via LinkedIn's native scheduler are not returned by the official Posts API. To sync these posts, configure the Voyager API credentials:

- `LINKEDIN_LI_AT`: The `li_at` cookie from a logged-in LinkedIn session
- `LINKEDIN_CSRF_TOKEN`: The `JSESSIONID` cookie value (without quotes)

To get the cookie values:
1. Log in to LinkedIn in your browser
2. Open Developer Tools > Application > Cookies
3. Copy the `li_at` and `JSESSIONID` values

When configured, the Voyager API is used first; if it returns no posts, the official API is used as fallback.

**Troubleshooting Voyager API errors:**

The Voyager API is LinkedIn's internal, undocumented API. It can break without notice. Common issues:

| Error | Cause | Solution |
|-------|-------|----------|
| 401/403 | Expired session cookies | Refresh `LINKEDIN_LI_AT` and `LINKEDIN_CSRF_TOKEN` from browser |
| 400 | Outdated `queryId` | Update `queryId` in `linkedin.py` (see below) |
| Empty response | API structure changed | Check if `included` array format changed |

To find a new `queryId`:
1. Open your company's LinkedIn admin page in browser
2. Open Developer Tools > Network tab
3. Look for requests to `voyager/api/graphql`
4. Copy the `queryId` parameter from the request URL

Current `queryId`: `voyagerFeedDashOrganizationalPageAdminUpdates.674de8f5f692ab9c9ce0ab819ecae05e`

### LinkedIn

Check [this article](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access) for details about
getting API access to LinkedIn.

*NOTE*: Reading posts from an organization requires [Marketing API access](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access#marketing).

1. Go to <https://www.linkedin.com/developers/tools/oauth>
2. Select the app you want to use
3. Select scope `r_organization_social`
4. Generate a token

### Slack

Create a Slack app in order to get API access: <https://api.slack.com/apps>.

Under OAuth & Permissions, set the following Bot Token Scopes:

- `channels:history` (public and/or private)
- `channels:read`
- `chat:write`

## Google Cloud Run

### Deploying the function

Check that the right files are uploaded:

```shell
❯ gcloud meta list-files-for-upload
sync.py
requirements.txt
slackc.py
linkedin.py
main.py
```

Deploy the function:

```shell
gcloud functions deploy <function-name> --gen2 --runtime=python312 --region=europe-west6 --source=. --trigger-topic=somesy
```

## Local development and testing

### Configure local environment

Create a `.env` file in the root of the project with the environment variables mentioned above:

```text
LINKEDIN_TOKEN=...
SLACK_TOKEN=...
...
```

Install the required packages and run the function locally:

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
python main_local.py
```

### Git Hooks

This project uses Git hooks to ensure code quality:

- **pre-commit**: Automatically formats, lints, and type-checks code before committing
- **pre-push**: Runs full test suite with coverage check before pushing to remote

Install the hooks with:

```shell
./scripts/install-hooks.sh
```

### Running tests and linting

Run the automated test suite:

```shell
pytest
```

Run a specific test file:

```shell
pytest tests/test_linkedin.py -v
```

Run tests with coverage:

```shell
pytest --cov=. --cov-report=term
```

Lint and check code quality:

```shell
ruff check .
```

Format code:

```shell
ruff format .
```

Check type hints:

```shell
mypy --ignore-missing-imports .
```
