from django.shortcuts import render
from dotenv import load_dotenv
from requests import post, get
import os

# load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback" # must be registered in spotify app
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
    return auth_url

# callback?
def callback(request):
    auth_code = request.get(auth_code)
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


# playlists
def playlists():
    pass

# rainbowify
def rainbowify():
    pass