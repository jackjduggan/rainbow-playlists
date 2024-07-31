from django.shortcuts import render
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback" # must be registered in spotify app

# index
def index():
    pass

# login
def login():
    pass

# callback?
def callback():
    pass

# playlists
def playlists():
    pass

# rainbowify
def rainbowify():
    pass