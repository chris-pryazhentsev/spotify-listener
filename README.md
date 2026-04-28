# spotify-listening

A tiny Flask service that redirects anyone who visits it to whatever you're currently playing on Spotify. If nothing is playing, it returns a plain-text message.

You can see this in action now at [listening.nyc.pryazhentsev.com](https://listening.nyc.pryazhentsev.com)

## Setup

### 1. Create a Spotify app

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create a new app.
2. Add `http://127.0.0.1:8888/callback` as a Redirect URI.
3. Copy the **Client ID** and **Client Secret**.

### 2. Authorize locally

Run the auth flow once on your local machine to generate a `.cache` token file:

```bash
cp .env.example .env
# fill in your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env

pip install spotipy
SPOTIPY_CLIENT_ID=... SPOTIPY_CLIENT_SECRET=... python test.py
```

After you authorize, a `.cache` file is written in the current directory containing your access and refresh tokens. The app will auto-refresh tokens from this file going forward.

### 3. Run with Docker

```bash
# .cache must exist in the project root (from the step above)
docker compose up -d
```

The service reads `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` from the environment (or a `.env` file) and mounts `.cache` as a volume so tokens persist across container restarts.

### Running without Docker

```bash
pip install -r requirements.txt
SPOTIPY_CLIENT_ID=... SPOTIPY_CLIENT_SECRET=... SPOTIPY_CACHE_PATH=.cache python app.py
```

## Configuration

| Environment variable   | Description                              | Default    |
|------------------------|------------------------------------------|------------|
| `SPOTIPY_CLIENT_ID`    | Spotify app client ID                    | required   |
| `SPOTIPY_CLIENT_SECRET`| Spotify app client secret                | required   |
| `SPOTIPY_CACHE_PATH`   | Path to the OAuth token cache file       | `/.cache`  |

## License

MIT
