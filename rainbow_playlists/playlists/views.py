from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from dotenv import load_dotenv
from colorthief import ColorThief
from requests import post, get
import numpy as np
import os, json, shutil, requests

# load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback" # must be registered in spotify app
SCOPES = "user-library-read playlist-read-private playlist-modify-public playlist-modify-private"

# index
def index(request):
    return render(request, 'index.html')

# login
def login(request):
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    # return render(auth_url) # this doesn't work as it expects a local template
    # instead, need to use redirect to go to an external page
    return redirect(auth_url)

# callback?
def callback(request):
    auth_code = request.GET.get('code')
    # debugging
    if not auth_code:
        return HttpResponse("No code provided", status=400)
    
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

    # Debugging: print the entire response data
    print(response_data)

    ## storing values across the session.
    request.session['access_token'] = response_data['access_token']
    request.session['refresh_token'] = response_data['refresh_token']
    return redirect(playlists)


# playlists
def playlists(request):
    # now that the token values are session-wide, they can be accessed
    access_token = request.session.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    url = "https://api.spotify.com/v1/me/playlists"
    response = get(url=url, headers=headers)
    json_result = json.loads(response.content)["items"]
    return render(request, 'playlists.html', {'playlists': json_result}) # TODO dont forget to add loop to template

# rainbowify
def rainbowify(request):
    # get the ID of the chosen playlist
    playlist_id = request.POST.get('playlist_id')
    # get the access token
    access_token = request.session.get('access_token')

    # generate response
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(access_token)
    result = get(url, headers=headers)

    tracks_json_result = result.json()["items"]

    # set images directory and reset
    images_directory = 'art_images/'
    reset_directory(images_directory)

    # download last available (smallest) version of album art available for each track
    for track in tracks_json_result:
        track_id = track['track']['id']
        album_image_url = track['track']['album']['images'][-1]['url']
        download_image(album_image_url, f"{track_id}_image.png")

    # extract dominant colours
    dominant_colors = {}
    for file in os.listdir(images_directory):
        dominant_color = get_dominant_color(file)
        dominant_colors[file] = dominant_color

    # import predefined colours array from 'colors.py'
    from .colors import colors
    # find predefined colour closest to each dominant colour using euclidean distances
    track_color_indices = []
    for filename, dominant_color in dominant_colors.items():
        closest_color_index = find_closest_predefined_color_index(dominant_color, colors)
        track_color_indices.append((filename, closest_color_index))

    # sort the tracks based on the colour indices
    track_color_indices.sort(key=lambda item: item[1])

    # sorted album covers contains (filname, dominant_color) tuples. Need to now map these filename's back to their track ID
    filename_to_track = {track['track']['id'] + "_image.png": track for track in tracks_json_result}

    # uris
    uris = []
    for filename, _ in track_color_indices:
        track = filename_to_track.get(filename)
        if track:
            uris.append(track["track"]["uri"])

    # get the user's user id (for playlist creation)
    user_id = get_user_name(access_token)

    # create the new, 'rainbowified' playlist (function returns playlist id)
    new_playlist_id = create_user_playlist(access_token, user_id)
    # and populate the new playlist with the sorted songs
    if new_playlist_id:
        populate_rainbow_playlist(access_token, new_playlist_id, uris)

    return redirect('playlists')

# Helper Functions
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def download_image(image_url, filename):
    response = requests.get(image_url, stream=True)
    with open(f"art_images/{filename}", "wb") as file:
        for chunk in response.iter_content(chunk_size=1024): # https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
                if chunk: # filter out keep-alive new chunks
                    file.write(chunk)

def reset_directory(dirname):
    # before adding images, first make sure the working directory is empty:
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    # recreate the directory:
    os.makedirs(dirname)

def get_dominant_color(image):
    ct = ColorThief(f"art_images/{image}")
    most_dominant_color = ct.get_color(quality=1)
    return most_dominant_color

def calculate_euclidean_distance(color1, color2):
    # r2, g2, b2 = predef_color[index_2][0], predef_color[index_2][1], predef_color[index_2][1]
    # e_d = (r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

def find_closest_predefined_color_index(dominant_color, colors):
    distances = [calculate_euclidean_distance(dominant_color, predefined_color) for predefined_color in colors]
    min_distance_index = distances.index(min(distances))
    return min_distance_index

def get_user_name(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["id"]
    return json_result

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