import json
from bs4 import BeautifulSoup
import lxml
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv("E:/Python/Environmental Variables/.env.txt")
CLIENT_ID = os.getenv("ClientID")
CLIENT_KEY = os.getenv("ClientSecret")
URL_REDIRECT = "http://127.0.0.1:9090"


# This section fetches and scrapes billboard top 100 and puts the songs into a list.

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")


response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/")

soup = BeautifulSoup(response.text, "lxml")
songs_span = soup.find_all(name="h3", id="title-of-a-story", class_="u-line-height-125")
songs = [song.getText().strip("\n\t") for song in songs_span]
artists = soup.find_all(name="span", class_="u-max-width-330")
artists_names = [name.getText().strip("\n\t") for name in artists]
songs_and_artist = dict(zip(songs, artists_names))
print(songs_and_artist)
#############################################################################################

# Authenticates user for Spotify API
spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_KEY,
        redirect_uri=URL_REDIRECT,
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt",
    ))

user_id = spotify.current_user()["id"]

# Searches Spotify for songs by title and artist
song_uris = []
for song in songs:
    #print(result)
    try:
        result = spotify.search(q=f"track:{song} year: {date[:4]}", type='track')
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
        print(f"Success! {song} was added.")
    except IndexError:
       print(f"{song} doesn't exist in spotify. Skipped.")
       pass


       #try:
       #    result = spotify.search(q=f"track:{song} year: {date[:4]}", type='track')
       #    uri = result["tracks"]["items"][0]["uri"]
       #    song_uris.append(uri)
       #except IndexError:
       #    print(f"{song} doesn't exist in spotify. Skipped.")

# Create a playlist in Spotify
playlist = spotify.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False,
                                        description=f"Python Script that scrapes Billboard 100 on {date}.")

# Add songs found into new playlist
spotify.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print(f"Playlist created on Spotify! {len(song_uris)} songs were successfully added.")