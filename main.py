import json
import requests
from pprint import pprint 
import time
from ably import AblyRest
'''
TODOs: For Playlist: Now Playing & Next Up monitor
-- Get Playlist of songs, given a Playlist ID (we will know which playlist we will play in advance) - Track Name, ID, Artist, Link, store in play order
-- Set token for full access scope
-- Print 'Now Playing & Next Up', find index of 'Now playing' ID in Playlist, return Next Up based on Playlist next index. Handle 'ID not in Playlist' error, but still return 'Now playing'
-- Handle  ValueError("No JSON object could be decoded") if no spotify player is detected
-- Check Spotify Token expiry, appears to have expired from one day to the next during testing

Extensions:
-- run for second playlist / channel
-- decide how to host this fundtion and update flask app

Youtube Tutorial reference: https://www.youtube.com/watch?v=yKz38ThJWqE
'''
with open("config.json", "r") as f:
    #Get config variables
    config = json.load(f)
    MW_SPOTIFY_TOKEN=config["MW_SPOTIFY_TOKEN"]
    SPOTIFY_CURRENT_TRACK_API = config["SPOTIFY_CURRENT_TRACK_API"]
    ABLY_KEY = config["ABLY_KEY"]

def get_current_track(access_token):
    #API Docs: Get Information About The User's Current Playback: https://developer.spotify.com/console/get-user-player/
    response = requests.get(
        SPOTIFY_CURRENT_TRACK_API,
        headers={
            "Authorization": "Bearer {}".format(access_token)
        }
    )
    resp_json=response.json()
    #print(resp_json)
    #Select the components we want for Track Name & Artist should do, but keep the ID and reference for now.
    track_id = resp_json["item"]["id"]
    track_name = resp_json["item"]["name"]
    #A track could have multiple artists, we just want one string of all their names, so join them together
    artists = resp_json["item"]["artists"]
    artists_names = ", ".join(artist['name'] for artist in artists)
    link = resp_json["item"]["external_urls"]["spotify"]

    return {
        "id": track_id,
        "name" : track_name,
        "artists": artists_names,
        "link": link
    }


def main():
    client = AblyRest(ABLY_KEY)
    #loop for testing    
    loop=0
    while loop<8:
        current_track_data = get_current_track(
            MW_SPOTIFY_TOKEN
        )
        print(current_track_data, " ",loop)

        message = "{} by {}".format(current_track_data["name"], current_track_data["artists"])
        print(message)
        channel = client.channels.get('spotify-monitor')
        channel.publish('update', message)

        loop+=1
        time.sleep(8)

if __name__ == "__main__":
    main()