# somesy - Development Guidelines

## Commands
- **Setup**: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-test.txt`
- **Run Manual Test**: `python main_test.py`
- **Run Unit Tests**: `pytest` or `pytest tests/test_linkedin.py -v` for a specific test file
- **Coverage**: `pytest --cov=. --cov-report=term` (requires pytest-cov)
- **Deploy**: `gcloud functions deploy somesy-uphill --gen2 --runtime=python312 --region=europe-west6 --source=. --trigger-topic=somesy`

## Code Style
- **Imports**: Standard library → third-party → local modules (blank line between groups)
- **Type Hints**: Always use type annotations for parameters and return values
- **Naming**: Snake case for variables/functions (e.g., `fetch_data`, `post_count`)
- **Error Handling**: Check HTTP status codes, provide defaults for env variables
- **Structure**: Keep modular approach (main.py, linkedin.py, slackc.py, sync.py)
- **Testing**: Use pytest fixtures for common test data/mocks

## Project
somesy is a serverless function that syncs LinkedIn posts to a Slack channel.
Dependencies: functions-framework, requests, slack_sdk, aiohttp (runtime)
and pytest, responses, pytest-mock (testing)
