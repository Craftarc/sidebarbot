import json
import os
import logging
import time
import requests
from datetime import datetime, timedelta, timezone
import praw
from prawcore.exceptions import InsufficientScope
from requests.exceptions import HTTPError


REQUIRED_SCOPES = ("wikiedit", "wikiread", "identity")

class Config:
    def __init__(self, config):
        self.client_id = config["auth"]["client_id"]
        self.client_secret = config["auth"]["client_secret"]
        self.refresh_token = config["auth"]["refresh_token"]
        self.user_agent = config["auth"]["user_agent"]

        self.loglevel = config.get("loglevel", "INFO")

        self.sub_name = config["sub_name"]

        self.pull_delay = config.get("pull_delay", 5) * 60 # in minutes

        self.micro_api_url = config["micro"]["api_url"]
        self.micro_specials_url = config["micro"]["specials_url"]
        self.micro_output_file = config["micro"]["output_file"]
        
        self.sidebar_start_marker = config["sidebar"]["start_marker"]
        self.sidebar_end_marker = config["sidebar"]["end_marker"]

my_name = None

def load_config():
    config_location = os.environ.get("CONFIG_FILE", "instance/config.json")

    with open(config_location) as f:
        config = json.load(f)
    
    return Config(config)

def connect(config):
    global my_name
    log.info("Connecting to reddit")

    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        refresh_token=config.refresh_token,
        user_agent=config.user_agent,
        )
    my_name = reddit.user.me(use_cache=True).name
    log.info(f"Connected as: {my_name}")
    return reddit

### FUNCTIONS

def update(reddit, subreddit, config):
    log.debug(f"Featching micro data")
    data = requests.get(config.micro_api_url, headers = { 'User-Agent': config.user_agent }).json()
    
    description = ""
    url = ""
    entries = data.get("entries")
    if not (entries is None) and len(entries) > 0:
        first = entries[0]
        if "description" in first and "url" in first:
            description = first["description"]   
            url = first["url"]
    
    if description != "" and url != "":
        new_micro_text = f"> [{description}]({url})"
        if not (entries is None) and len(entries) > 1:
           new_micro_text += f"[ and {str(len(entries) - 1)} more...]({config.micro_specials_url})"
        
        log.debug(new_micro_text)
        if not os.path.exists(config.micro_output_file):
            with open(config.micro_output_file, 'w'): pass
        
        f = open(config.micro_output_file, 'r+')
        old_micro_text = f.read()
        if old_micro_text != new_micro_text:
            log.info(f"Updating Sidebar: {new_micro_text}")
            f.seek(0)
            f.write(new_micro_text)

            sidebar = subreddit.wiki['config/sidebar']
            start = sidebar.content_md[0:sidebar.content_md.find(config.sidebar_start_marker)]
            end = sidebar.content_md[sidebar.content_md.find(config.sidebar_end_marker):]
            update_time = f"[Last updated at {time.strftime('%H:%M:%S UTC', time.gmtime())}](/smallText)"
            new_description = f"{start}{config.sidebar_start_marker}\n{new_micro_text}\n\n{update_time}\n\n{end}"
            sidebar.edit(new_description)
                
    log.debug(f"Sleeping for {config.pull_delay / 60.0} minutes")
    time.sleep(config.pull_delay)

### END FUNCTIONS

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

if __name__ == "__main__":
    config = load_config()

    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', datefmt='%y-%m-%d %H:%M:%S')
    log = logging.getLogger("dailydealsbot")
    log.setLevel(config.loglevel)
    log.info(f"Starting dailydealsbot with log level: {log.level}")

    try:
        reddit = connect(config)
        error_count = 0

        log.info(f"Getting subreddit {config.sub_name}")
        subreddit = reddit.subreddit(config.sub_name)

        while True:
            try:
                update(reddit, subreddit, config)
                error_count = 0
            except praw.exceptions.APIException:
                log.error(f"PRAW raised an API exception! Logging but ignoring.", exc_info=True)
                error_count = min(10, error_count+1)
            except HTTPError:
                log.error(f"requests raised an exception! Logging but ignoring.", exc_info=True)
                error_count = min(10, error_count+1)

            # in the case of an error, sleep longer and longer
            # one error, retry right away
            # more than one, delay a minute per consecutive error.
            # when reddit is down, this value will go up
            # when its just something like we cant reply to this deleted comment, try again right away
            time.sleep(max(0,error_count)*60)
    except InsufficientScope as e:
        log.error(f"PRAW raised InsufficientScope! Make sure you have the following scopes: {','.join(REQUIRED_SCOPES)}")
        raise e