from dotenv import load_dotenv
import requests
from requests import post, get
import numpy as np
import os, json, shutil
from colorthief import ColorThief

# load environment variables from .env file
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"  # Make sure to register this URL in your Spotify app settings

def get_auth_url():
    #scopes = "user-library-read playlist-read-private playlist-modify-public playlist-modify-private"
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

def download_image(image_url, filename):
    response = requests.get(image_url, stream=True)
    with open(f"art_images/{filename}", "wb") as file:
        for chunk in response.iter_content(chunk_size=1024): # https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
                if chunk: # filter out keep-alive new chunks
                    file.write(chunk)

def get_track_cover_art(token, track_id):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    filename = (f"{track_id}" + "_image.png")
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()["album"]["images"][-1]["url"]
    
    download_image(json_result, filename)

    print(json_result)
    return json_result

def get_dominant_color(image):
    ct = ColorThief(f"art_images/{image}")
    most_dominant_color = ct.get_color(quality=1)
    return most_dominant_color

def reset_directory(dirname):
    # before adding images, first make sure the working directory is empty:
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    # recreate the directory:
    os.makedirs(dirname)


#get_track_cover_art(token, "2VEZx7NWsZ1D0eJ4uv5Fym") # album art is Discovery by Daft Punk

# Download images for all tracks in the playlist
images_directory = 'art_images/'
reset_directory(images_directory)
for track in tracks:
    track_id = track['track']['id']
    get_track_cover_art(token, track_id)

"""
Loop through each image in the art_images/ directory and extract the dominant colour from it.
"""
def extract_dominant_colors():
    # images_directory = 'art_images/'

    dominant_colors = {}
    for file in os.listdir(images_directory):
        dominant_color = get_dominant_color(file)
        dominant_colors[file] = dominant_color
    return dominant_colors
# should produce a dictionary of { 'file': '(r,g,b)' }

dominant_colors = extract_dominant_colors()

"""
Calculate the euclidean distances between the dominant colours and the list of pre-defined colours
Assign the index (+1?) of the pre-def colour with the shortest euclidean distance to the album cover somehow?
"""

from colors import colors

def calculate_euclidean_distance(color1, color2):
    # r2, g2, b2 = predef_color[index_2][0], predef_color[index_2][1], predef_color[index_2][1]
    # e_d = (r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

def find_closest_predefined_color_index(dominant_color):
    distances = [calculate_euclidean_distance(dominant_color, predefined_color) for predefined_color in colors]
    min_distance_index = distances.index(min(distances))
    return min_distance_index

# Extract dominant colors and assign a sorting index based on the closest predefined color
track_color_indices = []
for filename, dominant_color in dominant_colors.items():
    closest_color_index = find_closest_predefined_color_index(dominant_color)
    track_color_indices.append((filename, closest_color_index))

# Sort the tracks based on the color indices
track_color_indices.sort(key=lambda item: item[1])

# for file, color in sorted_album_covers:
#     print(f"Album cover {file} has dominant color {color} and is closest to predefined color {find_closest_predefined_color(color)}")

"Sort by the indexes then, and in theory the album covers should be ordered...?"
"""
Album cover 0pQskrTITgmCMyr85tb9qq_image.png has dominant color (33, 29, 28) and is closest to predefined color (0, 0, 0)
Album cover 186hvCTyrni4KT9nwIQ7zS_image.png has dominant color (14, 14, 9) and is closest to predefined color (0, 0, 0)
Album cover 2cGxRwrMyEAp8dEbuZaVv6_image.png has dominant color (13, 14, 14) and is closest to predefined color (0, 0, 0)
...
"""

### -------------
# sorted album covers contains (filname, dominant_color) tuples. Need to now map these filename's back to their track ID
filename_to_track = {track['track']['id'] + "_image.png": track for track in tracks}

def create_user_playlist(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    data = {
        "name": "Your Rainbow Playlist",
        "description": "Made with Python",
        "public": False
    }

    result = post(url=url, headers=headers, json=data) # using the json parameter automatically serializes the data
    print(f"Executing.. with {data}")
    if result.status_code == 201:
        print("Playlist created successfully.")
        return result.json()["id"] # returns the playlist ID upon successful creation so we can add songs to it
    else:
        print(f"Failed to create playlist. Status code: {result.status_code}, Response: {result.json()}")
        return None


playlist_id = create_user_playlist(token, get_user_name(token))

def get_uris(tracks):
    uris = []
    for track in tracks:
        track = track["track"]
        uris.append(track["uri"])
    return uris

uris = []
for filename, _ in track_color_indices:
    track = filename_to_track.get(filename)
    if track:
        uris.append(track["track"]["uri"])

def populate_rainbow_playlist(token, playlist_id, uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    data = {
        "uris": uris
    }

    result = post(url=url, headers=headers, json=data)
    if result.status_code == 201:
        print("Tracks added successfully.")
    else:
        print(f"Failed to add tracks. Status code: {result.status_code}, Response: {result.json()}")

populate_rainbow_playlist(token, playlist_id, uris)

