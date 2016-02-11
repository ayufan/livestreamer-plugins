#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from livestreamer.plugin import Plugin
from livestreamer.plugin.api import http, validate
from livestreamer.stream import HTTPStream

PLAYLIST_URL="http://player.pl/api/?platform=ConnectedTV&terminal=Samsung&format=json&v=2.0&authKey=ba786b315508f0920eca1c34d65534cd&type=episode&id={video_id}&sort=newest&m=getItem&deviceScreenHeight=1080&deviceScreenWidth=1920"
_url_re = re.compile(r"^(?:https?:\/\/)?(?:www.)?player\.pl/[^\"]+,(?P<video_id>[0-9]+).html.*")
_playlist_schema = validate.Schema(
    {
        "item":{
            "videos":{
                "main":{
                    "video_content":validate.all([
                        {
                            "profile_name": validate.text,
                            "url": validate.url(scheme=validate.any("http"))
                        }
                    ])
                }
            }
        }
    },
    validate.get("item"),
    validate.get("videos"),
    validate.get("main"),
    validate.get("video_content")
)
QUALITY_MAP = {
    u"Standard": "720p",
    u"HD": "1080p",
    u"Bardzo wysoka": "1080p",
    u"Średnia": "720p",
    u"Wysoka": "640p",
    u"Niska": "512p",
    u"Bardzo niska": "320p",
}

class TvnPlayer(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)
        
    def _get_all_streams(self,video_content):
        for video in video_content:
            video_url = http.get(video["url"])
            quality = QUALITY_MAP[video["profile_name"]]
            stream =  HTTPStream(self.session, video_url.text)
            yield quality, stream
                        
    def _get_streams(self):
        url_match = _url_re.match(self.url)
        if url_match:
            video_id = url_match.group("video_id")
            res = http.get(PLAYLIST_URL.format(video_id=video_id))
            try:
                data = http.json(res, schema=_playlist_schema)
            except Exception:
                return None
            return self._get_all_streams(data)

__plugin__ = TvnPlayer

