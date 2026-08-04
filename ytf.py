import streamlit as st
import requests
from ytmusicapi import YTMusic

# --- 1. Page Configuration ---
st.set_page_config(page_title="YouTube Lunjir Downloader", page_icon="🎵")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-header { text-align: center; color: #ff0000; font-weight: bold; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# Initialize the YouTube Music API (Synchronous and fast)
ytmusic = YTMusic()

# --- 2. Backend: Cobalt API Logic ---
def download_audio_api(video_url):
    api_url = "https://api.cobalt.tools/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": video_url,
        "downloadMode": "audio",
        "audioFormat": "mp3" 
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        data = response.json()
        
        if data.get("status") in ["stream", "redirect", "tunnel"]:
            return data.get("url"), None
        elif data.get("status") == "error":
             return None, data.get("text", "Unknown API error occurred.")
        else:
            return None, "API blocked the request."
    except Exception as e:
        return None, f"Network Error: {str(e)}"

# --- 3. UI: Header & Search Bar ---
st.markdown("<h2 class='main-header'>🎵 YouTube Lunjir Downloader</h2>", unsafe_allow_html=True)

search_query = st.text_input("Lunjir amen tok ik non (Enter song name or link):", placeholder="e.g., Main hoon saath tere")

if st.button("Search"):
    if search_query:
        with st.spinner("Searching YouTube Music..."):
            try:
                # Search strictly for songs using ytmusicapi
                search_results = ytmusic.search(search_query, filter="songs", limit=5)
                
                if search_results:
                    st.session_state.search_results = search_results
                else:
                    st.warning("No results found.")
            except Exception as e:
                st.error(f"Search failed: {str(e)}")

# --- 4. UI: Display Search Results ---
if "search_results" in st.session_state:
    st.write("### Search Results:")
    
    for idx, video in enumerate(st.session_state.search_results):
        # ytmusicapi uses 'videoId' instead of 'link'
        video_id = video.get('videoId')
        if not video_id:
            continue
            
        # Reconstruct the standard YouTube URL for Cobalt
        full_url = f"https://www.youtube.com/watch?v={video_id}"
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Grab the highest resolution thumbnail available
            thumbnail_url = video['thumbnails'][-1]['url']
            st.image(thumbnail_url, use_container_width=True)
            
        with col2:
            title = video.get('title', 'Unknown Title')
            
            # Safely extract the artist name
            artist = "Unknown Artist"
            if video.get('artists') and len(video['artists']) > 0:
                artist = video['artists'][0].get('name', 'Unknown Artist')
                
            duration = video.get('duration', 'Unknown')
            
            st.write(f"**{title}**")
            st.write(f"Artist: {artist} | Duration: {duration}")
            
            if st.button(f"Convert to MP3", key=f"convert_{idx}"):
                with st.spinner("Converting on Cobalt servers..."):
                    audio_link, error_msg = download_audio_api(full_url)
                    
                    if audio_link:
                        st.success("✅ Conversion Complete!")
                        st.markdown(f"### [➡️ Click Here to Download MP3]({audio_link})")
                    else:
                        st.error(f"Error: {error_msg}")
        
        st.markdown("---")
