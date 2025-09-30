import streamlit as st
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from typing import List, Dict, Tuple
import os
import tempfile

# Configure Streamlit page
st.set_page_config(
    page_title="YouTube Music to Spotify Transfer", page_icon="🎵", layout="wide"
)

# Initialize session state variables
if "youtube" not in st.session_state:
    st.session_state.youtube = None
if "spotify" not in st.session_state:
    st.session_state.spotify = None
if "playlists" not in st.session_state:
    st.session_state.playlists = None
if "selected_playlist" not in st.session_state:
    st.session_state.selected_playlist = None
if "transfer_complete" not in st.session_state:
    st.session_state.transfer_complete = False
if "unmatched_songs" not in st.session_state:
    st.session_state.unmatched_songs = []
if "youtube_token" not in st.session_state:
    st.session_state.youtube_token = None


def initialize_youtube_oauth(client_secrets_dict: dict):
    """Initialize YouTube with OAuth credentials."""
    try:
        # Create a temporary file for client secrets
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(client_secrets_dict, f)
            temp_file = f.name

        # Use InstalledAppFlow for local OAuth
        flow = InstalledAppFlow.from_client_secrets_file(
            temp_file, scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )

        # Run local server for OAuth (will open browser automatically)
        credentials = flow.run_local_server(port=0, prompt="consent")

        # Clean up temp file
        os.unlink(temp_file)

        # Build YouTube client
        youtube = build("youtube", "v3", credentials=credentials)

        # Save credentials to session state for reuse
        st.session_state.youtube_token = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        return youtube
    except Exception as e:
        st.error(f"Error initializing YouTube: {str(e)}")
        return None


def initialize_youtube_from_token(token_info: dict):
    """Initialize YouTube from saved token."""
    try:
        credentials = Credentials(
            token=token_info["token"],
            refresh_token=token_info["refresh_token"],
            token_uri=token_info["token_uri"],
            client_id=token_info["client_id"],
            client_secret=token_info["client_secret"],
            scopes=token_info["scopes"],
        )
        youtube = build("youtube", "v3", credentials=credentials)
        return youtube
    except Exception as e:
        st.error(f"Error initializing YouTube from token: {str(e)}")
        return None


def initialize_spotify(
    client_id: str, client_secret: str, redirect_uri: str
) -> spotipy.Spotify:
    """Initialize Spotify client with OAuth2 authentication."""
    try:
        scope = "playlist-modify-public playlist-modify-private"

        # Clear old cache if it exists
        cache_path = ".spotify_cache"
        if os.path.exists(cache_path):
            os.remove(cache_path)

        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=cache_path,
            open_browser=True,
        )
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        return spotify
    except Exception as e:
        st.error(f"Error initializing Spotify: {str(e)}")
        return None


def get_youtube_playlists(youtube) -> List[Dict]:
    """Fetch all playlists from YouTube."""
    try:
        playlists = []
        request = youtube.playlists().list(
            part="snippet,contentDetails", mine=True, maxResults=50
        )

        while request:
            response = request.execute()

            for item in response.get("items", []):
                playlists.append(
                    {
                        "id": item["id"],
                        "title": item["snippet"]["title"],
                        "count": item["contentDetails"]["itemCount"],
                    }
                )

            request = youtube.playlists().list_next(request, response)

        return playlists
    except Exception as e:
        st.error(f"Error fetching playlists: {str(e)}")
        return []


def get_playlist_tracks(youtube, playlist_id: str) -> List[Tuple[str, str]]:
    """Fetch all tracks from a YouTube playlist."""
    try:
        tracks = []
        request = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50
        )

        while request:
            response = request.execute()

            for item in response.get("items", []):
                title = item["snippet"]["title"]
                # Try to extract artist from title (common format: "Artist - Song Title")
                if " - " in title:
                    parts = title.split(" - ", 1)
                    artist = parts[0].strip()
                    song_title = parts[1].strip()
                else:
                    # Use channel name as artist fallback
                    artist = (
                        item["snippet"]
                        .get("videoOwnerChannelTitle", "")
                        .replace(" - Topic", "")
                    )
                    song_title = title

                if song_title and artist:
                    tracks.append((song_title, artist))

            request = youtube.playlistItems().list_next(request, response)

        return tracks
    except Exception as e:
        st.error(f"Error fetching playlist tracks: {str(e)}")
        return []


def search_spotify_track(spotify: spotipy.Spotify, title: str, artist: str) -> str:
    """Search for a track on Spotify and return the best match URI."""
    try:
        # Clean up title and artist
        title = (
            title.replace("(Official Video)", "")
            .replace("(Official Audio)", "")
            .strip()
        )
        artist = artist.replace(" - Topic", "").strip()

        # Search with both title and artist
        query = f"{title} {artist}"
        results = spotify.search(q=query, type="track", limit=5)

        if results["tracks"]["items"]:
            return results["tracks"]["items"][0]["uri"]

        # If no results, try with just the title
        results = spotify.search(q=title, type="track", limit=5)

        if results["tracks"]["items"]:
            return results["tracks"]["items"][0]["uri"]

        return None
    except Exception as e:
        return None


def create_spotify_playlist(spotify: spotipy.Spotify, name: str) -> str:
    """Create a new playlist on Spotify and return its ID."""
    try:
        user_id = spotify.current_user()["id"]
        playlist = spotify.user_playlist_create(
            user=user_id,
            name=name,
            public=True,
            description=f"Transferred from YouTube Music",
        )
        return playlist["id"]
    except Exception as e:
        st.error(f"Error creating playlist: {str(e)}")
        return None


def add_tracks_to_spotify_playlist(
    spotify: spotipy.Spotify, playlist_id: str, track_uris: List[str]
):
    """Add tracks to a Spotify playlist in batches."""
    try:
        # Spotify allows adding 100 tracks at a time
        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i : i + batch_size]
            spotify.playlist_add_items(playlist_id, batch)
            time.sleep(0.5)  # Rate limiting
    except Exception as e:
        st.error(f"Error adding tracks to playlist: {str(e)}")


def transfer_playlist(
    youtube, spotify: spotipy.Spotify, playlist_id: str, playlist_name: str
) -> Tuple[int, List[Tuple[str, str]]]:
    """Transfer a playlist from YouTube to Spotify."""
    # Get tracks from YouTube
    yt_tracks = get_playlist_tracks(youtube, playlist_id)

    if not yt_tracks:
        st.error("No tracks found in the selected playlist.")
        return 0, []

    st.info(f"Found {len(yt_tracks)} tracks in YouTube playlist.")

    # Create Spotify playlist
    spotify_playlist_id = create_spotify_playlist(spotify, playlist_name)

    if not spotify_playlist_id:
        return 0, []

    # Search and collect Spotify track URIs
    spotify_uris = []
    unmatched = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, (title, artist) in enumerate(yt_tracks):
        status_text.text(
            f"Processing: {title} by {artist} ({idx + 1}/{len(yt_tracks)})"
        )

        spotify_uri = search_spotify_track(spotify, title, artist)

        if spotify_uri:
            spotify_uris.append(spotify_uri)
        else:
            unmatched.append((title, artist))

        progress_bar.progress((idx + 1) / len(yt_tracks))
        time.sleep(0.3)  # Rate limiting

    # Add all matched tracks to Spotify playlist
    if spotify_uris:
        status_text.text("Adding tracks to Spotify playlist...")
        add_tracks_to_spotify_playlist(spotify, spotify_playlist_id, spotify_uris)

    progress_bar.empty()
    status_text.empty()

    return len(spotify_uris), unmatched


# Main UI
st.title("🎵 YouTube Music to Spotify Playlist Transfer")
st.markdown("Transfer your playlists from YouTube Music to Spotify seamlessly.")

# Sidebar for authentication
with st.sidebar:
    st.header("Authentication")

    # YouTube Authentication
    st.subheader("1. YouTube Music")
    st.info("YouTube requires OAuth authentication to access your playlists")

    uploaded_credentials = st.file_uploader(
        "Upload OAuth client_secrets.json",
        type=["json"],
        help="Download from Google Cloud Console",
        key="youtube_upload",
    )

    if uploaded_credentials and st.session_state.youtube is None:
        if st.button("🔐 Authorize YouTube"):
            try:
                client_secrets = json.load(uploaded_credentials)
                with st.spinner("Opening browser for authorization..."):
                    st.session_state.youtube = initialize_youtube_oauth(client_secrets)
                    if st.session_state.youtube:
                        st.success("✅ YouTube connected!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Check if we have a saved token
    elif st.session_state.youtube_token and st.session_state.youtube is None:
        st.session_state.youtube = initialize_youtube_from_token(
            st.session_state.youtube_token
        )
        if st.session_state.youtube:
            st.success("✅ YouTube connected!")

    # Show status if connected
    if st.session_state.youtube:
        st.success("✅ YouTube connected!")
        if st.button("Disconnect YouTube"):
            st.session_state.youtube = None
            st.session_state.youtube_token = None
            st.session_state.playlists = None
            st.rerun()

    st.markdown("---")

    # Spotify Authentication
    st.subheader("2. Spotify")

    client_id = st.text_input("Client ID", type="password", key="spotify_client_id")
    client_secret = st.text_input(
        "Client Secret", type="password", key="spotify_client_secret"
    )

    # Use the Streamlit default redirect URI
    redirect_uri = "http://127.0.0.1:8501"

    st.info(f"✅ Using redirect URI: `{redirect_uri}`")
    st.caption("Make sure this exact URI is added in your Spotify Dashboard")

    if st.button("Connect to Spotify"):
        if client_id and client_secret:
            with st.spinner("Opening browser for Spotify authorization..."):
                st.session_state.spotify = initialize_spotify(
                    client_id, client_secret, redirect_uri
                )
                if st.session_state.spotify:
                    try:
                        user = st.session_state.spotify.current_user()
                        st.success(f"✅ Connected as {user['display_name']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Authentication failed: {str(e)}")
                        st.info(
                            "After authorizing in the browser, copy the full URL and paste it back here."
                        )
        else:
            st.warning("Please fill in all Spotify credentials.")

    # Show status if connected
    if st.session_state.spotify:
        try:
            user = st.session_state.spotify.current_user()
            st.success(f"✅ Connected as {user['display_name']}")
            if st.button("Disconnect Spotify"):
                st.session_state.spotify = None
                if os.path.exists(".spotify_cache"):
                    os.remove(".spotify_cache")
                st.rerun()
        except:
            st.session_state.spotify = None

# Main content area
if st.session_state.youtube and st.session_state.spotify:
    st.success("🎉 Both services connected! Ready to transfer playlists.")

    # Fetch playlists if not already loaded
    if st.session_state.playlists is None:
        with st.spinner("Loading your YouTube playlists..."):
            st.session_state.playlists = get_youtube_playlists(st.session_state.youtube)

    if st.session_state.playlists:
        st.subheader("Select a Playlist to Transfer")

        # Create a list of playlist names for the selectbox
        playlist_names = [
            f"{p['title']} ({p.get('count', 0)} tracks)"
            for p in st.session_state.playlists
        ]

        selected_idx = st.selectbox(
            "Choose a playlist:",
            range(len(playlist_names)),
            format_func=lambda x: playlist_names[x],
        )

        selected_playlist = st.session_state.playlists[selected_idx]

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**Playlist:** {selected_playlist['title']}")
            st.write(f"**Tracks:** {selected_playlist.get('count', 'Unknown')}")

        with col2:
            if st.button("🚀 Start Transfer", type="primary"):
                with st.spinner("Transferring playlist..."):
                    matched_count, unmatched = transfer_playlist(
                        st.session_state.youtube,
                        st.session_state.spotify,
                        selected_playlist["id"],
                        selected_playlist["title"],
                    )

                    st.session_state.transfer_complete = True
                    st.session_state.unmatched_songs = unmatched

                    st.success(
                        f"✅ Transfer complete! {matched_count} tracks added to Spotify."
                    )

                    if unmatched:
                        st.warning(
                            f"⚠️ {len(unmatched)} tracks could not be matched on Spotify."
                        )

        # Display unmatched songs if any
        if st.session_state.transfer_complete and st.session_state.unmatched_songs:
            st.subheader("Unmatched Songs")

            unmatched_text = "\n".join(
                [
                    f"{title} - {artist}"
                    for title, artist in st.session_state.unmatched_songs
                ]
            )

            st.text_area(
                "Songs not found on Spotify:", value=unmatched_text, height=200
            )

            st.download_button(
                label="📥 Download Unmatched Songs",
                data=unmatched_text,
                file_name="unmatched_songs.txt",
                mime="text/plain",
            )
    else:
        st.warning("No playlists found in your YouTube account.")

elif st.session_state.youtube and not st.session_state.spotify:
    st.info("👈 Please connect to Spotify in the sidebar to continue.")

elif not st.session_state.youtube and st.session_state.spotify:
    st.info("👈 Please connect to YouTube in the sidebar to continue.")

else:
    st.info(
        "👈 Please authenticate with both YouTube and Spotify in the sidebar to get started."
    )

    with st.expander("ℹ️ How to get YouTube OAuth credentials"):
        st.markdown("""
        1. Go to https://console.cloud.google.com/
        2. Create a new project or select existing one
        3. Enable **YouTube Data API v3**
        4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
        5. Choose **Desktop app** as application type
        6. Download the JSON file (client_secrets.json)
        7. Upload it above and click "Authorize YouTube"

        ⚠️ **Note:** API Keys don't work for accessing your playlists - you must use OAuth!
        """)

    with st.expander("ℹ️ How to get Spotify API credentials"):
        st.markdown("""
        1. Go to https://developer.spotify.com/dashboard
        2. Log in and create a new app
        3. Copy the **Client ID** and **Client Secret**
        4. Click **Edit Settings**
        5. Add **exactly** this Redirect URI: `http://127.0.0.1:8501`
        6. Save and enter credentials in the sidebar

        ⚠️ **Important:** The redirect URI must match exactly (including the port 8501)!
        """)
