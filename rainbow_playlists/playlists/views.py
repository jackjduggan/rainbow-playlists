from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from dotenv import load_dotenv
import requests
from requests import post, get
import os, json

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
def rainbowify():
    pass