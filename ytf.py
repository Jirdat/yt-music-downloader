import streamlit as st
import requests
from youtubesearchpython import VideosSearch

# --- 1. Page Configuration ---
st.set_page_config(page_title="YouTube Lunjir Downloader", page_icon="🎵")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-header { text-align: center; color: #ff0000; font-weight: bold; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

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
        with st.spinner("Searching YouTube..."):
            try:
                # Fetch the top 5 results for the search term
                videosSearch = VideosSearch(search_query, limit=5)
                st.session_state.search_results = videosSearch.result()['result']
            except Exception as e:
                st.error("Search failed. Please try again.")

# --- 4. UI: Display Search Results ---
if "search_results" in st.session_state:
    st.write("### Search Results:")
    
    for idx, video in enumerate(st.session_state.search_results):
        # Create two columns: one for the thumbnail, one for the title/button
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display the video thumbnail
            st.image(video['thumbnails'][0]['url'], use_container_width=True)
            
        with col2:
            # Display title and channel
            st.write(f"**{video['title']}**")
            st.write(f"Channel: {video['channel']['name']} | Duration: {video['duration']}")
            
            # Unique button for every video in the list
            if st.button(f"Convert to MP3", key=f"convert_{idx}"):
                with st.spinner("Converting on Cobalt servers..."):
                    audio_link, error_msg = download_audio_api(video['link'])
                    
                    if audio_link:
                        st.success("✅ Conversion Complete!")
                        # Provide a direct clickable link to download the file
                        st.markdown(f"### [➡️ Click Here to Download MP3]({audio_link})")
                    else:
                        st.error(f"Error: {error_msg}")
        
        st.markdown("---") # Add a dividing line between videos
