# YouTube Music ➔ Spotify Playlist Sync

Easily copy your YouTube Music playlist to Spotify using this Streamlit web app!
**No coding required. Works locally and can be deployed to Streamlit Cloud.**

---

## Features

- Upload your YouTube Music Chrome header file (for authentication)
- Enter your Spotify API credentials (Client ID, Secret, Redirect URI)
- Select any of your YouTube Music playlists
- Instantly copy all available playlist tracks to a new Spotify playlist
- Download a list of missing/unmatched songs
- No sensitive info stored; runs per-session in browser

---

## 1. Prerequisites

- **Python 3.8+** installed on your machine

---

## 2. Setup Instructions

### Step 1: Clone or Download This Project

```
git clone https://github.com/your-username/ytmusic-to-spotify.git
cd ytmusic-to-spotify
```
Or simply download and unzip.

### Step 2: Install Dependencies

```
pip install -r requirements.txt
```


---

## 3. Export YouTube Music Auth Headers

1. Open **Chrome** and log in to [YouTube Music](https://music.youtube.com).
2. Press `F12` to open Developer Tools.
3. Go to the **Network** tab. Search/Filter for requests with “browse”.
4. Click a playlist, find a “browse” request, right click → **Copy** > **Copy request headers**.
5. Paste the headers into a new file called:
    ```
    ytmusic_headers_auth.json
    ```
   The format should match [ytmusicapi header export instructions](https://ytmusicapi.readthedocs.io/en/latest/setup.html).
6. You will be prompted to upload this file in the app when running!

---

## 4. Get Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Log in and **create a new app**.
3. Copy your **Client ID** and **Client Secret**.
4. Add a Redirect URI; e.g., `http://localhost:8501` (must match value in code/app).
5. Save these credentials — you'll enter them in the app when prompted.

---

## 5. Run the App Locally

```
streamlit run app.py
```

- This will launch the app at:


```
http://localhost:8501
```

- Open the link in your browser.

---

## 6. Usage: Step-by-Step

1. **Upload your YouTube Music chrome header file** (ytmusic_headers_auth.json)
2. **Enter Spotify credentials** (Client ID, Client Secret, Redirect URI)
3. **Select your playlist** from the dropdown
4. **Click "Sync!"**
 The app will create a new playlist in your Spotify account with song matches.
5. **Optional:** Download a `.txt` file of any songs not found on Spotify.

---

## FAQ

**Q: Does this store my credentials or playlist data?**
A: No. All processing is in-session (temporary files). Credentials and data are not saved or shared.

**Q: Does it support deployment online?**
A: Yes. You can deploy to [Streamlit Cloud](https://streamlit.io/cloud) (just upload your repo and set up as above).
File upload and Spotify credential entry is per user/session.

**Q: What if the app says "No playlists found"?**
A: Ensure you've uploaded the correct headers file and your YouTube Music account has at least one playlist.

**Q: Why are some tracks missing on Spotify?**
A: Not all tracks in YouTube Music are available or exactly match on Spotify.

---

**For issues and contributions, open an issue or PR on this repo!**

---

Made by Shubham Misra, 2025.
