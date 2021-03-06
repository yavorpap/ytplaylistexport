#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name:        ui
# Purpose:
#
# Author:      Yavor
#
# Created:
# Copyright:   (c) Yavor
# Licence:     GLPv3
#-------------------------------------------------------------------------------
from __future__ import print_function

import httplib2
import os

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


class PlaylistManager():
    YTPLAYLIST_SECRETS_FILE = "client_secrets.json"
    YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    YTPLAYLIST_MISSING_FILES_WARNING = "Some files required for authenticating to the Youtube API are missing. " +\
                                       "Please consult README if in doubt."

    def __init__(self, is_console):
        self.flow = None
        self.storage = None
        self.credentials = None
        self.yt_service = None
        self.api_key = None
        self.__is_logged_in = False
        self.is_console = is_console
        self.ui = None
        if self.is_console:
            self.parse_str = ["--noauth_local_webserver"]
        else:
            self.parse_str = []

    def destroy_credentials(self):
        if not self.is_logged_in:
            raise RuntimeError("Not logged in!")
        os.remove("oauth2.json")

    def check_files(self):
        if not os.path.isfile("client_secrets.json") or not os.path.isfile("api_key.txt"):
            self.ui.display_warning("Missing files", self.YTPLAYLIST_MISSING_FILES_WARNING)

    def login(self):
        self.check_files()
        self.flow = flow_from_clientsecrets(self.YTPLAYLIST_SECRETS_FILE,
                                            scope=self.YOUTUBE_READ_WRITE_SCOPE)
        self.storage = Storage("oauth2.json")
        self.credentials = self.storage.get()
        if self.credentials is None or self.credentials.invalid:
            flags = argparser.parse_args(self.parse_str)
            self.credentials = run_flow(self.flow, self.storage, flags)
        self.yt_service = build(self.YOUTUBE_API_SERVICE_NAME,
                                self.YOUTUBE_API_VERSION,
                                http=self.credentials.authorize(
                                    httplib2.Http()))
        self.__is_logged_in = True

    def skip_login(self):
        self.check_files()
        self.__is_logged_in = False
        self.yt_service = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION)
        with open("api_key.txt") as f:
            self.api_key = f.read()

    @property
    def is_logged_in(self):
        return self.__is_logged_in

    def list_playlists(self, username=None):
        if username:
            prev_request = self.yt_service.channels().\
                list(part="id", forUsername=username, key=self.api_key)
            prev_response = prev_request.execute()
            if "items" not in prev_response or\
                            len(prev_response["items"]) == 0:
                return None
            channel_id = prev_response["items"][0]["id"]
            request = self.yt_service.playlists().\
                list(part="snippet", maxResults=50, channelId=channel_id, key=self.api_key)
        else:
            request = self.yt_service.playlists().\
                list(part="snippet", mine=True, maxResults=50)
        result = request.execute()
        return result["items"]

    def export_playlist(self, playlist_id, local_filename):
        total_result = []
        kwargs = {"playlistId": playlist_id, "part": "snippet", "maxResults": 50}
        if not self.is_logged_in:
            kwargs["key"] = self.api_key
        while True:
            request = self.yt_service.playlistItems().list(**kwargs)
            result = request.execute()
            total_result.extend(result["items"])
            if "nextPageToken" not in result:
                break
            next_token = result["nextPageToken"]
            kwargs["pageToken"] = next_token
        f = open(local_filename, 'w')
        print(u"[playlist]".encode('utf-8'), file=f)
        print(u"NumberOfEntries={0}".format(len(total_result)).encode('utf-8'), file=f)
        for (i, item) in enumerate(total_result):
            data = item["snippet"]
            print(u"Title{0}={1}".format(i+1, data["title"]).encode('utf-8'), file=f)
            print(u"File{0}=http://youtube.com/watch?v={1}".
                  format(i+1, data["resourceId"]["videoId"]).encode('utf-8'),
                  file=f)
        f.close()

