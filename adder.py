#!/usr/bin/python
import sys
import spotipy
import spotipy.util as util
import time
import logging
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import requests

logging.basicConfig(format='%(asctime)s %(message)s', 
        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

load_dotenv() # optional .env file

failurecount = 0
expb = 1

playlist_id = os.getenv("PLAYLIST_ID")
scope = ['user-read-currently-playing', 
        'playlist-modify-public',
        'playlist-modify-private'
        ]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

logging.info("Fetching all tracks ...")
pl = sp.playlist_tracks(playlist_id)
tracks = [x["track"]["id"] for x in pl["items"]]
while(pl["next"]):
    pl = sp.next(pl)
    tracks.extend([x["track"]["id"] for x in pl["items"]])

logging.info("Found %s tracks", len(tracks))


while True:
    try:
        cur = sp.currently_playing()
        expb = 1
        if cur is None:
            # logging.info("Currently not playing anything")
            time.sleep(90)
        else:
            if cur["item"] is not None:
                trackid = cur["item"]["id"]
                if trackid not in tracks:
                    sp.playlist_add_items(playlist_id, [trackid], position=None)
                    tracks.append(trackid)
                    logging.info("Adding track: %s - %s",
                            cur["item"]["artists"][0]["name"], cur["item"]["name"])
            # else:
            #     logging.info("Item is in playlist already")
    except (requests.ConnectionError, requests.ReadTimeout):
        failurecount += 1
        logging.error("Connection error, expb: %d, total failures: %d", expb, failurecount)
        if expb == 1:
            expb = 2
            continue
        elif expb == 2:
            expb = 4
            time.sleep(60)
            continue
        elif expb == 4:
            expb = 8
            time.sleep(600)
            continue
        else:
            logging.error("Failed too often")
            exit(1)
    # except TypeError:
    #     logging.error("cur: %s", cur)
    #     time.sleep(5)
    #     continue
    # except Exception as e:
    #     logging.error("%s", e)
    #     logging.error("General error?")
    #     failurecount += 1
    #     logging.error("Failures: %d", failurecount)
    #     time.sleep(300)
    #     continue
    time.sleep(30)
