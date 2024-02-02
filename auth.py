import base64
import praw
import os

from util import parse
import config

config = config.load_config()
N_BYTES = 43  # Makes state string 64 bytes


def generate_state():
    """
    Generate a random base64url encoded string to use as state
    """
    random_bytes = os.urandom(N_BYTES)

    encoded = base64.b64encode(random_bytes)

    url_safe = encoded.decode('utf-8').replace('+',
                                               '-').replace('/', '_').replace('=', '')

    return url_safe

def save_refresh_token(refresh_token):
    """
    Saves the refresh token in a file
    """
    with open("refresh_token.txt", "w", encoding="utf-8") as file:
        file.write(refresh_token)

def login():
    """
    Start the oauth process
    @return Instance of praw.Reddit
    """
    print("Initiating authorisation process...")
    # Skip login if there is already a refresh token
    if os.path.exists("refresh_token.txt"):
        print("Using refresh token...")
        with open("refresh_token.txt", "r", encoding="utf-8") as file:
            refresh_token = file.read()

        reddit = praw.Reddit(
            client_id=config["auth"]["client_id"],
            client_secret=config["auth"]["client_secret"],
            refresh_token=refresh_token,
            user_agent=config["auth"]["user_agent"])

        print("Oauth successful!")
        return reddit

    else:
        # Otherwise do the entire Oauth flow
        reddit = praw.Reddit(
            client_id=config["auth"]["client_id"],
            client_secret=config["auth"]["client_secret"],
            redirect_uri=config["auth"]["redirect_uri"],
            user_agent=config["auth"]["user_agent"])

        state = generate_state()
        auth_url = reddit.auth.url(scopes=["*"], state=state, duration="permanent")

        # Point user to initial auth url
        print("Please click on the link below to authenticate")
        print(auth_url)

        # After user returns from browser
        raw = input("Please paste the entire string from the browser URL bar: \n")
        query_dict = parse.get_query_parameters(raw)

        code = query_dict["code"][0] # Only one element
        state_to_check = query_dict["state"][0]

        # Check state hash
        if state == state_to_check:
            # Save the refresh token
            refresh_token = reddit.auth.authorize(code)
            save_refresh_token(refresh_token)
            print("Oauth successful!")
            return reddit