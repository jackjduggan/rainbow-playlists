"""
This module houses the configuration for the 'playlists' app.
"""

from django.apps import AppConfig


class PlaylistsConfig(AppConfig):
    """
    This class manages the configuration for 'playlists'
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'playlists'
