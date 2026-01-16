import dotenv

import sync

_ = dotenv.load_dotenv(verbose=True, override=True)
sync.linkedin_to_slack(2 * 24)
