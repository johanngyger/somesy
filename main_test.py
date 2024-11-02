from dotenv import load_dotenv

import sync

_ = load_dotenv()
sync.linkedin_to_slack(7*24)
