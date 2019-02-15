# rocketdump: scrape all public rocketchat channels
# usage: python rocketdump.py > rocketdump.out
# requires python 3 and with the ``requests`` library

from functools import partial
import json
from multiprocessing.dummy import Pool
import os
import sys

import requests


ROCKET_CHAT_API = "https://magenta.rocket.chat/api/v1/"
LIST_URL = ROCKET_CHAT_API + "channels.list"
MESSAGES_URL = ROCKET_CHAT_API + "channels.messages"


def dump_channel_msgs(channel, headers):
    return requests.get(
        MESSAGES_URL, params={"roomName": channel, "count": 0}, headers=headers
    ).json()


if __name__ == "__main__":
    token = os.getenv("ROCKETCHAT_TOKEN", False)
    user_id = os.getenv("ROCKETCHAT_USER_ID", False)
    if not (token and user_id):
        print(
            "You need to set the ROCKETCHAT_TOKEN and ROCKETCHAT_USER_ID"
            " environment variables. To get them, (1) open Rocket Chat (2)"
            " go to My Account, and (3) generate a new Personal Access Token",
            file=sys.stderr,
        )
        sys.exit(1)

    headers = {"X-Auth-Token": token, "X-User-Id": user_id}
    r = requests.get(LIST_URL, params={"count": 0}, headers=headers)
    channels = [c["name"] for c in r.json()["channels"]]

    with Pool() as p:
        dumps = list(p.map(partial(dump_channel_msgs, headers=headers), channels))

    print(json.dumps(dumps))
