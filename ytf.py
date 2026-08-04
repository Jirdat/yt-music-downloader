import streamlit as st
import requests
import asyncio
from py_yt import VideosSearch

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

# --- 3. Backend: Async Search Function ---
async def perform_search(query):
    # Initialize the search for 5 videos using the py-yt-search library
    videosSearch = VideosSearch(query, limit=5, language='en', region='US')
    # Fetch the results asynchronously
    result = await videosSearch.next()
    return result.get('result', [])

# --- 4. UI: Header & Search Bar ---
st.markdown("<h2 class='main-header'>🎵 YouTube Lunjir Downloader</h2>", unsafe_allow_html=True)

search_query = st.text_input("Lunjir amen tok ik non (Enter song name or link):", placeholder="e.g., Main hoon saath tere")

if st.button("Search"):
    if search_query:
        with st.spinner("Searching YouTube..."):
            try:
                # Use asyncio.run to execute the async search function
                search_results = asyncio.run(perform_search(search_query))
                
                if search_results:
                    st.session_state.search_results = search_results
                else:
                    st.warning("No results found or search was blocked.")
            except Exception as e:
                st.error(f"Search failed: {str(e)}")

# --- 5. UI: Display Search Results ---
if "search_results" in st.session_state:
    st.write("### Search Results:")
    
    for idx, video in enumerate(st.session_state.search_results):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(video['thumbnails'][0]['url'], use_container_width=True)
            
        with col2:
            st.write(f"**{video['title']}**")
            st.write(f"Channel: {video['channel']['name']} | Duration: {video['duration']}")
            
            if st.button(f"Convert to MP3", key=f"convert_{idx}"):
                with st.spinner("Converting on Cobalt servers..."):
                    audio_link, error_msg = download_audio_api(video['link'])
                    
                    if audio_link:
                        st.success("✅ Conversion Complete!")
                        st.markdown(f"### [➡️ Click Here to Download MP3]({audio_link})")
                    else:
                        st.error(f"Error: {error_msg}")
        
        st.markdown("---")
