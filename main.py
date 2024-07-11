from dotenv import load_dotenv
from requests import post, get
import os, base64, json

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

print("Go to the following URL to authorize the application:")
print(get_auth_url())

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

def get_user_playlist_id(token, playlist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    # construct our query
    query = f"?q={playlist_name}&type=playlist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    return json_result

def get_user_playlists(token):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result



# --- --- --- --- --- ---
print("Go to the following URL to authorize the application:")
print(get_auth_url())

auth_code = input("Enter the authorization code you received from Spotify: ")
token = get_access_token(auth_code)