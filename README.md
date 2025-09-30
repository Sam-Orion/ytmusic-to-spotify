# 🎵 YouTube Music to Spotify Playlist Transfer

A simple Streamlit web application that allows you to transfer playlists from YouTube Music to Spotify with just a few clicks.

## ✨ Features

- 🔐 OAuth authentication for both YouTube and Spotify
- 📋 View all your YouTube Music playlists
- 🎯 Select and transfer any playlist to Spotify
- 🔍 Automatic song matching between platforms
- 📊 Progress tracking during transfer
- ⚠️ Lists unmatched songs that couldn't be found on Spotify
- 💾 Download unmatched songs as a text file
- 🎨 Clean and intuitive user interface

## 📋 Prerequisites

- Python 3.7 or higher
- A Google Cloud Platform account (for YouTube API access)
- A Spotify Developer account
- Active YouTube Music and Spotify accounts

## 🚀 Installation

1. **Clone or download this repository**

2. **Install required packages:**
```bash
pip install streamlit google-api-python-client google-auth-oauthlib spotipy
```

3. **Run the application:**
```bash
streamlit run app.py
```

The app will open in your default browser at `http://127.0.0.1:8501`

## 🔑 Setup Instructions

### YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**:
  - Navigate to "APIs & Services" → "Library"
  - Search for "YouTube Data API v3"
  - Click "Enable"
4. Create OAuth 2.0 credentials:
  - Go to "APIs & Services" → "Credentials"
  - Click "Create Credentials" → "OAuth 2.0 Client ID"
  - Choose **Desktop app** as the application type
  - Give it a name (e.g., "YouTube Music Transfer")
  - Click "Create"
5. Download the JSON file (it will be named something like `client_secret_xxxxx.json`)
6. Rename it to `client_secrets.json` (optional, but recommended)

### Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
  - App name: (e.g., "YouTube to Spotify Transfer")
  - App description: (e.g., "Transfer playlists from YouTube")
5. Click "Create"
6. Copy your **Client ID** and **Client Secret**
7. Click "Edit Settings"
8. Under "Redirect URIs", add exactly:
```
  http://127.0.0.1:8501
```
9. Click "Add" and then "Save"

## 📖 Usage

### Step 1: Authenticate with YouTube

1. In the sidebar, upload your `client_secrets.json` file
2. Click "🔐 Authorize YouTube"
3. A browser window will open asking you to sign in to Google
4. Grant the necessary permissions
5. The app will automatically connect once authorized

### Step 2: Authenticate with Spotify

1. Enter your Spotify **Client ID**
2. Enter your Spotify **Client Secret**
3. Click "Connect to Spotify"
4. A browser window will open asking you to sign in to Spotify
5. Grant the necessary permissions
6. You'll be redirected back to the app

### Step 3: Transfer a Playlist

1. Once both services are connected, your YouTube playlists will load
2. Select the playlist you want to transfer from the dropdown
3. Click "🚀 Start Transfer"
4. Watch the progress as songs are matched and added to Spotify
5. A new playlist with the same name will be created in your Spotify account

### Step 4: Review Results

- The app will show how many songs were successfully transferred
- If any songs couldn't be matched, they'll be listed
- You can download a text file of unmatched songs for manual review

## ⚠️ Important Notes

### YouTube API Limitations

- **API Key authentication does NOT work** for accessing your playlists - you must use OAuth
- The YouTube Data API has a daily quota limit (10,000 units/day for free tier)
- Reading a playlist typically uses 1-5 units per request

### Song Matching

- The app attempts to match songs by title and artist
- Some songs may not be found on Spotify if:
 - They're not available in your region
 - The title/artist format is different
 - They're not on Spotify
- The app will list all unmatched songs so you can add them manually

### Privacy & Security

- Your credentials are only used locally and are not stored or transmitted anywhere
- OAuth tokens are cached locally in `.spotify_cache` and session state
- You can disconnect either service at any time using the disconnect buttons

## 🐛 Troubleshooting

### "The request uses the mine parameter but is not properly authorized"
- This means you're trying to use an API Key instead of OAuth
- YouTube requires OAuth authentication to access your personal playlists
- Upload the OAuth `client_secrets.json` file instead

### "Address already in use" (Spotify)
- The redirect URI is hardcoded to `http://127.0.0.1:8501`
- Make sure this exact URI is in your Spotify app settings
- Close any other applications using port 8501

### "No playlists found"
- Make sure you've authorized the app correctly
- Check that you have playlists in your YouTube Music library
- Try disconnecting and reconnecting

### Songs not matching
- Some mismatches are normal due to different catalogs
- Try manually searching for unmatched songs on Spotify
- The app provides a downloadable list of unmatched songs

## 📝 File Structure
```
.
├── app.py                  # Main application file
├── README.md              # This file
├── .spotify_cache         # Spotify auth cache (auto-generated)
└── temp_ytmusic_auth.json # Temporary YouTube auth (auto-generated)
```

## 🔒 Security Best Practices

1. **Never share your credentials** or OAuth files publicly
2. **Add these to .gitignore** if using version control:
```
  .spotify_cache
  temp_*.json
  client_secrets.json
```
3. **Revoke access** from the respective dashboards when done:
  - Google: https://myaccount.google.com/permissions
  - Spotify: https://www.spotify.com/account/apps/

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available under the MIT License.

## 💡 Tips

- **Large playlists**: The transfer process respects API rate limits, so large playlists may take a few minutes
- **Duplicate prevention**: The app creates a new playlist each time you transfer. If you want to update an existing playlist, delete it first
- **Best results**: Playlists with well-formatted titles (Artist - Song) tend to match better
- **Region restrictions**: Some songs may not be available in your Spotify region

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your API credentials are correct
3. Ensure both services are properly authenticated
4. Check the Streamlit console for detailed error messages

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [Spotipy](https://spotipy.readthedocs.io/) for Spotify API
- Uses [Google API Python Client](https://github.com/googleapis/google-api-python-client) for YouTube API

---

Made with ❤️ for music lovers who want to migrate their playlists seamlessly!
