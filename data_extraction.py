
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import boto3
import json
from datetime import datetime


def lambda_handler(event, context):

    auth_manager = SpotifyOAuth(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        redirect_uri="http://127.0.0.1:8889/callback",
        scope="playlist-read-private",
        cache_path=None
    )

    token_info = auth_manager.refresh_access_token(
        os.environ["refresh_token"]
    )

    sp = spotipy.Spotify(
        auth=token_info["access_token"]
    )

    playlist_link = "https://open.spotify.com/playlist/0kg3Niymj7CG4ArhD6lN7W"
    playlist_URI = playlist_link.split("/")[-1]

    spotify_data = sp._get(
        f"playlists/{playlist_URI}/items",
        limit=50,
        offset=0
    )

    cilent = boto3.client('s3')
    filename = "spotify_raw_" + str(datetime.now()) + ".json"

    cilent.put_object(
        Bucket="spotify-etl-project-gaurav-ambasta",
        Key="raw_data/to_processed/" + filename,
        Body=json.dumps(spotify_data)
        
    )

    return {
        "statusCode": 200,
        "body": {
            "total_items": spotify_data.get("total"),
            "items_returned": len(spotify_data.get("items", []))
        }
    }