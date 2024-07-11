from dotenv import load_dotenv
from requests import post, get
import os, base64, json
from colorthief import ColorThief

# load environment variables from .env file
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"  # Make sure to register this URL in your Spotify app settings

def get_auth_url():
    scopes = "user-library-read playlist-read-private"
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&scope={scopes}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return auth_url

def get_access_token(auth_code):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = post(url, headers=headers, data=data)
    response_data = response.json()
    return response_data["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# --- --- --- --- --- ---
def get_user_name(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)["id"]

    return json_result

def get_user_playlists(token):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    json_result_owned = [playlist for playlist in json_result if playlist["owner"]["id"] == get_user_name(token) ]
    
    return json_result_owned

def display_user_playlists(playlists):
    for playlist in playlists:
        print(f"{playlist["name"]}, id={playlist["id"]}")
        playlistList.append((playlist["id"], playlist["name"]))

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()["items"]
    
    # print(json_result)
    return json_result

def display_tracks_in_playlist(tracks):
    for idx, item in enumerate(tracks):
        track = item["track"]
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}, id={track['id']}")

# --- --- --- --- --- ---

print("Go to the following URL to authorize the application:")
print(get_auth_url())

auth_code = input("Enter the authorization code you received from Spotify: ")
token = get_access_token(auth_code)

playlists = get_user_playlists(token)
playlistList = []
display_user_playlists(playlists)

choice = input("Enter the id of the playlist you wish to rainbow-ify: ")

tracks = get_playlist_tracks(token, choice)

# Display tracks
print(f"You selected: {[playlist for playlist in playlistList if playlist[0] == choice][0][1]}")
display_tracks_in_playlist(tracks)

def get_track_cover_art(token, track_id):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()["album"]["images"][-1]["url"]
    
    print(json_result)
    return json_result


def get_dominant_color(image):
    ct = ColorThief(f"images/{image}")
    most_dominant_color = ct.get_color(quality=1)

get_track_cover_art(token, "2VEZx7NWsZ1D0eJ4uv5Fym")