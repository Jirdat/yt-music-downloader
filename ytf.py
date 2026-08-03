import streamlit as st
import requests

# --- 1. Page Configuration ---
st.set_page_config(page_title="YouTube Lunjir Downloader", page_icon="🎵")

# --- 2. Custom CSS Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        text-align: center;
        color: #ff0000;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #28a745;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Backend: Cobalt API Logic ---
def download_audio_api(video_url):
    """
    Sends the YouTube URL to the Cobalt API and returns the direct MP3 link.
    """
    # The Cobalt processing endpoint
    api_url = "https://api.cobalt.tools/"
    
    # Cobalt strictly requires these headers for POST requests
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # The updated payload configuring the exact audio file we want
    payload = {
        "url": video_url,
        "downloadMode": "audio", # Tell Cobalt we only want audio
        "audioFormat": "mp3"     # Tell Cobalt to format it as an MP3
    }
    
    try:
        # Send the request to Cobalt's servers
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Parse the JSON response
        data = response.json()
        
        # Cobalt will return a status of 'tunnel', 'stream', or 'redirect' upon success
        if data.get("status") in ["stream", "redirect", "tunnel"]:
            # Return the direct download link provided by the API
            return data.get("url"), None
        elif data.get("status") == "error":
             return None, data.get("text", "Unknown API error occurred.")
        else:
            return None, "API blocked the request or the video is unavailable."
            
    except Exception as e:
        return None, f"Network Error: {str(e)}"

# --- 4. UI: Header ---
st.markdown("<h2 class='main-header'>🎵 YouTube Lunjir Downloader</h2>", unsafe_allow_html=True)

# --- 5. UI: Search Bar & Download Button ---
with st.form("search_form"):
    # The text input for the YouTube link
    search_query = st.text_input("Lunjir amen tok ik non:", placeholder="Paste YouTube link here...")
    
    # The submit button
    submit_button = st.form_submit_button(label="Convert to MP3")
    
if submit_button and search_query:
    # Save the URL to the session state
    st.session_state.selected_url = search_query
    
    with st.spinner("Converting... Please wait"):
        # Call the API function
        audio_link, error_msg = download_audio_api(st.session_state.selected_url)

        if audio_link:
            st.success("Ready to download!")
            
            # Streamlit fetches the MP3 directly from the Cobalt link
            st.download_button(
                label="Download MP3",
                data=requests.get(audio_link).content,
                file_name="audio.mp3",
                mime="audio/mpeg"
            )
        else:
            st.error(f"Error: {error_msg}")
            
