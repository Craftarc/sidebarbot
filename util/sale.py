import requests
import json
from datetime import datetime
import config

config = config.load_config()
def get_sale_info():
    """
    Get the current sale information
    @return: JSON: Response JSON containing sale information
    """
    url = config["api"]["sale"]

    # Pretend to be a browser so CloudFlare doesn't block us
    response = requests.get(url, headers={"user-agent": "Mozilla/5"})

    # Get the list of items on sale
    json_object = json.loads(response.text)
    return json_object["entries"]

def is_stash_sale(item_info):
    """
    @param item_info: JSON object containing sale information for one item
    @return true if an item is describing a stash sale
    """
    name = item_info["microtransaction"]["name"]
    return config["parse_target"] in str.lower(name)

def get_start_date(item_info):
    return datetime.fromisoformat(item_info["startAt"])

def get_end_date(item_info):
    return datetime.fromisoformat(item_info["endAt"])


def get_current_stash_sale_dates():
    """
    @return: datetime: The start and end dates for the stash sale, None if there is no
    stash sale currently
    """
    items = get_sale_info()
    for item in items:
        if is_stash_sale(item):
            return get_start_date(item), get_end_date(item)

    return None