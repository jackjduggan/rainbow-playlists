"""
This module contains views and helper functions for the Rainbow Playlists Django application.
The application allows users to log in with their Spotify account, view their playlists,
and create a new playlist where tracks are sorted based on the dominant colors of their album art.
"""

import os
import json
import shutil
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from colorthief import ColorThief
from requests import post, get
import numpy as np
from .colors import colors

# load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback" # must be registered in spotify app
SCOPES = "user-library-read playlist-read-private playlist-modify-public playlist-modify-private"

def index(request):
    """
    Render the index page.

    :param request: HttpRequest object
    :return: HttpResponse object rendering 'index.html'
    """
    return render(request, 'index.html')


def login():
    """
    Redirect the user to the Spotify login page.

    :param request: HttpRequest object
    :return: HttpResponse object redirecting to the Spotify authorization URL
    """
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    # return render(auth_url) # this doesn't work as it expects a local template
    # instead, need to use redirect to go to an external page
    return redirect(auth_url)


def callback(request):
    """
    Handle the Spotify authorization callback.

    :param request: HttpRequest object
    :return: HttpResponse object redirecting to the playlists view
    """
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
    response = post(url, headers=headers, data=data, timeout=10)
    response_data = response.json()

    # Debugging: print the entire response data
    print(response_data)

    ## storing values across the session.
    request.session['access_token'] = response_data['access_token']
    request.session['refresh_token'] = response_data['refresh_token']
    return redirect(playlists)


def playlists(request):
    """
    Display the user's Spotify playlists.

    :param request: HttpRequest object
    :return: HttpResponse object rendering 'playlists.html' with the user's playlists
    """
    # now that the token values are session-wide, they can be accessed
    access_token = request.session.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    url = "https://api.spotify.com/v1/me/playlists"
    response = get(url=url, headers=headers, timeout=10)
    json_result = json.loads(response.content)["items"]
    return render(request, 'playlists.html', {'playlists': json_result})


def rainbowify(request):
    """
    Create a new playlist with tracks sorted by the dominant colors of their album art.

    :param request: HttpRequest object
    :return: HttpResponse object redirecting to the playlists view
    """
    # get the ID of the chosen playlist
    playlist_id = request.POST.get('playlist_id')
    # get the access token
    access_token = request.session.get('access_token')

    # generate response
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(access_token)
    result = get(url, headers=headers, timeout=10)

    tracks_json_result = result.json()["items"]

    # set images directory and reset
    reset_directory('art_images/')

    # download last available (smallest) version of album art available for each track
    for track in tracks_json_result:
        track_id = track['track']['id']
        album_image_url = track['track']['album']['images'][-1]['url']
        download_image(album_image_url, f"{track_id}_image.png")

    # find predefined colour closest to each dominant colour using euclidean distances
    track_color_indices = []
    for filename, dominant_color in dominant_colors.items():
        closest_color_index = find_closest_predefined_color_index(dominant_color)
        track_color_indices.append((filename, closest_color_index))

    # sort the tracks based on the colour indices
    track_color_indices.sort(key=lambda item: item[1])

    # sorted album covers contains (filname, dominant_color) tuples
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
    """
    Get the authorization header for Spotify API requests.

    :param token: Spotify access token
    :return: Dictionary containing the authorization header
    """
    return {"Authorization": "Bearer " + token}


def download_image(image_url, filename):
    """
    Download an image from a URL.

    :param image_url: URL of the image
    :param filename: Name of the file to save the image as
    """
    response = requests.get(image_url, stream=True, timeout=10)
    with open(f"art_images/{filename}", "wb") as file:
        for chunk in response.iter_content(chunk_size=1024): # ref1
            if chunk: # filter out keep-alive new chunks
                file.write(chunk)


def reset_directory(dirname):
    """
    Reset a directory by deleting and recreating it.

    :param dirname: Name of the directory to reset
    """
    # before adding images, first make sure the working directory is empty:
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    # recreate the directory:
    os.makedirs(dirname)


def get_dominant_color(image):
    """
    Get the dominant color from an image.

    :param image: Name of the image file
    :return: Tuple representing the RGB values of the dominant color
    """
    ct = ColorThief(f"art_images/{image}")
    most_dominant_color = ct.get_color(quality=1)
    return most_dominant_color


def calculate_euclidean_distance(color1, color2):
    """
    Calculate the Euclidean distance between two colors.

    :param color1: Tuple representing the RGB values of the first color
    :param color2: Tuple representing the RGB values of the second color
    :return: Euclidean distance between the two colors
    """
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

def extract_dominant_colors():
    """
    Extract the dominant colors from the downloaded album images.

    :return: Dictionary mapping filenames to dominant colors
    """
    dominant_colors = {}
    for file in os.listdir('art_images/'):
        dominant_color = get_dominant_color(file)
        dominant_colors[file] = dominant_color
    return dominant_colors

def find_closest_predefined_color_index(dominant_color):
    """
    Find the index of the predefined color closest to the given dominant color.

    :param dominant_color: Tuple representing the RGB values of the dominant color
    :param colors: List of predefined colors
    :return: Index of the closest predefined color
    """
    distances = [calculate_euclidean_distance(
        dominant_color, predefined_color) for predefined_color in colors]
    min_distance_index = distances.index(min(distances))
    return min_distance_index


def get_user_name(token):
    """
    Get the Spotify user ID of the authenticated user.

    :param token: Spotify access token
    :return: User ID of the authenticated user
    """
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = get(url, headers=headers, timeout=10)
    json_result = json.loads(result.content)["id"]
    return json_result


def create_user_playlist(token, user_id):
    """
    Create a new playlist for the user.

    :param token: Spotify access token
    :param user_id: Spotify user ID
    :return: ID of the created playlist, or None if the creation failed
    """
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    data = {
        "name": "Your Rainbow Playlist",
        "description": "Made with Python",
        "public": False
    }

    result = post(url=url, headers=headers, json=data, timeout=10)
    print(f"Executing.. with {data}")
    if result.status_code == 201:
        print("Playlist created successfully.")
        # returns the playlist ID upon successful creation
        return result.json()["id"]
    print(f"Playlist creation error. Code: {result.status_code}, Response: {result.json()}")
    return None


def populate_rainbow_playlist(token, playlist_id, uris):
    """
    Populate the playlist with the given URIs.

    :param token: Spotify access token
    :param playlist_id: ID of the playlist to populate
    :param uris: List of track URIs to add to the playlist
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    data = {"uris": uris}

    result = post(url=url, headers=headers, json=data, timeout=10)
    if result.status_code == 201:
        print("Tracks added successfully.")
    else:
        print(f"Failed to add tracks. Status code: {result.status_code}, Response: {result.json()}")

# ref1: https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
# note: docstrings written by generative AI.
