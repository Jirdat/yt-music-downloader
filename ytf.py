import streamlit as st
import yt_dlp
import os
import tempfile
import requests

st.set_page_config(page_title="YT Lunjir Downloader", page_icon="🎵", layout="centered")

# --- Inject Custom CSS ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Silently pass if CSS is missing so it doesn't break the app

st.markdown("""<div style="position: static; text-align: right; margin-bottom: 1px"><a href="https://www.instagram.com/jirdat_timung?igsh=MWFlaG15Y2t4Zjlyaw==" target="_blank"><button class="follow">Follow Us</button></a></div>""", unsafe_allow_html=True)
local_css("design.css")

st.title("🎵 YouTube Lunjir Downloader")

# --- 1. Initialize State ---
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_url' not in st.session_state:
    st.session_state.selected_url = None
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = None
if 'downloaded_file' not in st.session_state:
    st.session_state.downloaded_file = None

# --- 2. Callback Function ---
def select_song(url, title):
    st.session_state.selected_url = url
    st.session_state.selected_title = title
    st.session_state.downloaded_file = None

# --- 3. Core Functions ---
def search_youtube(query, max_results=5):
    ydl_opts = {'extract_flat': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_string = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_string, download=False)
            return info.get('entries', [])
        except Exception as e:
            st.error(f"Lonle, Internet connect tha: {e}")
            return []


def download_audio_api(video_url):
    # The public Cobalt API endpoint
    api_url = "https://api.cobalt.tools/api/json"
    
    # Cobalt strictly requires these headers for POST requests
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # The payload configuring the exact audio file we want
    payload = {
        "url": video_url,
        "isAudioOnly": True,
        "aFormat": "mp3" 
    }
    
    try:
        # Send the request to Cobalt's servers
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Parse the JSON response
        data = response.json()
        
        # Cobalt will return a status of 'stream' or 'redirect' upon success
        if data.get("status") in ["stream", "redirect"]:
            # Return the direct download link provided by the API
            return data.get("url"), None
        else:
            return None, "API blocked the request or the video is unavailable."
            
    except Exception as e:
        return None, f"Network Error: {str(e)}"
        

# --- 4. UI: Search Bar ---
with st.form("search_form"):
    search_query = st.text_input("Lunjir amen tok ik non:")
    submitted = st.form_submit_button("Ritarlip")

if submitted:
    if search_query.strip():
        with st.spinner("Ri tarlip voi lang..."):
            st.session_state.search_results = search_youtube(search_query)
            st.session_state.selected_url = None 
            st.session_state.downloaded_file = None
    else:
        st.warning("Choklim Alunjir amen tok ji han chiningri lo.")

# --- 5. UI: Download Processor (MOVED TO THE TOP) ---
if st.session_state.selected_url:
    st.write(f"### Preparing: {st.session_state.selected_title}")
    
    if st.session_state.downloaded_file is None:
        with st.spinner("Alunjir kabahak lapen mp3 along ka convert.... (Chonghon paningding ik tha)..."):
            file_path, error_msg = download_audio_mp3(st.session_state.selected_url)
            
            if file_path and os.path.exists(file_path):
                st.session_state.downloaded_file = file_path
                st.rerun() 
            else:
                st.error(f"MP3 Conversion failed! Error: {error_msg}")
                st.session_state.selected_url = None
    
    if st.session_state.downloaded_file:
        st.success("MP3 ready lo!")
        with open(st.session_state.downloaded_file, "rb") as file:
            st.download_button(
                label="💾 Dak ber ik non",
                data=file,
                file_name=f"{st.session_state.selected_title}.mp3",
                mime="audio/mpeg" 
            )
        st.divider() # Adds a nice visual line to separate the download from the search results

# --- 6. UI: Search Results (MOVED TO THE BOTTOM) ---
if st.session_state.search_results:
    st.write("### Chongvai ik non aber")
    
    for video in st.session_state.search_results:
        title = video.get('title', 'Unknown Title')
        video_id = video.get('id')
        url = video.get('url', f"https://www.youtube.com/watch?v={video_id}")
        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else None
        
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                if thumbnail:
                    st.image(thumbnail, width=250)
            with col2:
                st.markdown(f"<div style='font-size: 14px;'>{title}</div>", unsafe_allow_html=True)

                st.button(
                    "Download",
                    key=f"btn_{video_id}",
                    on_click=select_song,
                    args=(url,title)
                )



st.markdown("""<div class="developer">Developed by Jirdat</div>""", unsafe_allow_html=True)
