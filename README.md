# somesy – social media sync

![somesy](logo/somesy_200px.jpg)

A serverless Google Cloud Run function that syncs LinkedIn posts to a Slack channel.

## Configuration

The following environment variables are required:

- `LINKEDIN_TOKEN`: LinkedIn OAuth token
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

Create a Slack app in order to get API access: <https://api.slack.com/apps>.

Under OAuth & Permissions, set the following Bot Token Scopes:

- `channels:history` (public and/or private)
- `channels:read`
- `chat:write`

## Google Cloud Run

### Deploying the function

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
