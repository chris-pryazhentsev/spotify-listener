import os
import threading
import time
import logging
from flask import Flask, redirect, Response, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

POLL_INTERVAL = 15
SCOPE = "user-read-currently-playing"

current_track: dict[str, str | None] = {"url": None, "name": None}
lock = threading.Lock()

auth_manager = SpotifyOAuth(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
    redirect_uri=os.environ.get("REDIRECT_URI", "http://127.0.0.1:8080/callback"),
    scope=SCOPE,
    cache_path=os.environ.get("SPOTIPY_CACHE_PATH", "/.cache"),
    open_browser=False,
)
sp = spotipy.Spotify(auth_manager=auth_manager)


def is_authorized() -> bool:
    try:
        return auth_manager.get_cached_token() is not None
    except Exception:
        return False


def poll_spotify():
    while True:
        try:
            if is_authorized():
                result = sp.currently_playing()
                if result and result.get("is_playing") and result.get("item"):
                    track = result["item"]
                    url = track["external_urls"]["spotify"]
                    name = track["name"]
                    artists = ", ".join(a["name"] for a in track["artists"])
                    with lock:
                        current_track["url"] = url
                        current_track["name"] = f"{name} — {artists}"
                    logging.info("Now playing: %s", current_track["name"])
                else:
                    with lock:
                        current_track["url"] = None
                        current_track["name"] = None
                    logging.info("Nothing playing")
            else:
                logging.info("Not authorized yet — visit /auth to connect Spotify")
        except Exception:
            logging.exception("Error polling Spotify")
        time.sleep(POLL_INTERVAL)


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


@app.route("/")
def index():
    if not is_authorized():
        return redirect(url_for("authorize"))
    with lock:
        url = current_track["url"]
    if url:
        return redirect(url)
    return Response("Nothing is currently playing.", status=200, content_type="text/plain; charset=utf-8")


@app.route("/auth")
def authorize():
    return redirect(auth_manager.get_authorize_url())


@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return Response(f"Authorization failed: {error}", status=400, content_type="text/plain; charset=utf-8")
    code = request.args.get("code")
    auth_manager.get_access_token(code, as_dict=False, check_cache=False)
    return redirect(url_for("index"))


if __name__ == "__main__":
    t = threading.Thread(target=poll_spotify, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=8080)
