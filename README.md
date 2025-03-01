# rainbow-playlists
by Jack Duggan

[![Pylint](https://github.com/jackjduggan/rainbow-playlists/actions/workflows/pylint.yml/badge.svg)](https://github.com/jackjduggan/rainbow-playlists/actions/workflows/pylint.yml)

This project is a work in progress

On initial run of the app, the user is greeted with a screen prompting them to login with Spotify. This login buttons redirects them to the official Spotify authentication URL, and then back to the app once they've logged in.
![alt text](images/login_screen.png)

Upon successful login, the user is presented with a list of playlists, pulled from their Spotify account. The user need only select the 'Rainbowify' button beside any of these playlists. This kicks off a process in which the contents of that playlist are requested, and the album art for each track downloaded. The most dominant colour is extracted from each of these album arts, which are then sorted based on that dominant colour.
![alt text](images/playlists_screen.png)

A new playlist is created within the user's Spotify account with the same songs (100 maximum, unfortunately), however the order of the songs will differ, sorted in rainbow-fashion.
![alt text](images/rainbow_playlist.png)