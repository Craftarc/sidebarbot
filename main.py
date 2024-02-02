import time
from util import poereddit
import config
import auth
import logging
from datetime import datetime

if __name__ == "__main__":
    config = config.load_config()
    logging.basicConfig(level=logging.INFO)

    # Get a Reddit instance
    reddit = auth.login()
    print(f"Logged in as {reddit.user.me()}")

    # Update sidebar with stash tab sale dates
    while True:
        poereddit.update_sidebar(reddit)

        # Log to console
        current_date = datetime.now()
        formatted_date = current_date.strftime('%d %B %Y')
        print(f"Updated sidebar now: {formatted_date}")

        # Update again the next day
        time.sleep(86400) # 24h
