import streamlit as st
import requests

# --- 1. Page Configuration ---
st.set_page_config(page_title="YouTube Lunjir Downloader", page_icon="🎵")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-header { text-align: center; color: #ff0000; font-weight: bold; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. Backend: Cobalt API for Downloading ---
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

# --- 3. Backend: Piped API for Searching ---
def search_youtube(query):
    # This queries an open-source proxy server instead of YouTube directly
    search_url = f"https://pipedapi.kavin.rocks/search?q={query}&filter=all"
    
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Filter out channels/playlists, keep only video streams, return top 5
            videos = [item for item in data.get("items", []) if item.get("type") == "stream"]
            return videos[:5]
        return []
    except Exception:
        return []

# --- 4. UI: Header & Search Bar ---
st.markdown("<h2 class='main-header'>🎵 YouTube Lunjir Downloader</h2>", unsafe_allow_html=True)

search_query = st.text_input("Lunjir amen tok ik non (Enter song name or link):", placeholder="e.g., Main hoon saath tere")

if st.button("Search"):
    if search_query:
        with st.spinner("Searching via proxy API..."):
            search_results = search_youtube(search_query)
            
            if search_results:
                st.session_state.search_results = search_results
            else:
                st.warning("No results found. Please try a different search term.")

# --- 5. UI: Display Search Results ---
if "search_results" in st.session_state:
    st.write("### Search Results:")
    
    for idx, video in enumerate(st.session_state.search_results):
        # Piped API returns URLs like '/watch?v=...'
        short_url = video.get('url', '')
        if not short_url:
            continue
            
        full_url = f"https://www.youtube.com{short_url}"
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(video.get('thumbnail', ''), use_container_width=True)
            
        with col2:
            st.write(f"**{video.get('title', 'Unknown Title')}**")
            st.write(f"Channel: {video.get('uploaderName', 'Unknown')} | Duration: {video.get('duration', 0)} seconds")
            
            if st.button(f"Convert to MP3", key=f"convert_{idx}"):
                with st.spinner("Converting on Cobalt servers..."):
                    audio_link, error_msg = download_audio_api(full_url)
                    
                    if audio_link:
                        st.success("✅ Conversion Complete!")
                        st.markdown(f"### [➡️ Click Here to Download MP3]({audio_link})")
                    else:
                        st.error(f"Error: {error_msg}")
        
        st.markdown("---")
        
