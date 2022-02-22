#!/usr/bin/python
import sys
import spotipy
import spotipy.util as util
import pprint
import time
import logging
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


pp=pprint.PrettyPrinter(indent=4)
logging.basicConfig(format='%(asctime)s %(message)s', 
        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

load_dotenv() # optional .env file

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
    cur = sp.currently_playing()
    if cur is None:
        logging.info("Currently not playing anything")
        time.sleep(110)
    else:
        trackid = cur["item"]["id"]
        if trackid not in tracks:
            tracks.append(trackid)
            logging.info("Adding track: %s - %s",
                    cur["item"]["artists"][0]["name"], cur["item"]["name"])
            sp.playlist_add_items(playlist_id, [trackid], position=None)
        # else:
        #     logging.info("Item is in playlist already")
    time.sleep(10)
