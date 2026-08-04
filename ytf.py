import streamlit as st
import requests

# --- 1. Page Configuration ---
st.set_page_config(page_title="YouTube Lunjir Downloader", page_icon="🎵")

# Function to load external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load your custom style.css file
local_css("design.css")

st.markdown("""<button style='border: solid black; padding:10px; border-radius: 6px; background-color: pink'><a href="" style='font-size:12px; text-decoration: none; color: white'>Follow Us</a></button>""", unsafe_allow_html=True)

# --- 2. Backend: RapidAPI for Downloading ---
def download_audio_api(video_id):
    try:
        rapid_key = st.secrets["RAPID_API_KEY"]
    except KeyError:
        return None, "RapidAPI Key missing! Please add RAPID_API_KEY to Streamlit Secrets."

    # The specific RapidAPI endpoint for YouTube MP3 conversion
    url = "https://youtube-mp36.p.rapidapi.com/dl"
    
    # We pass the video ID to the API
    querystring = {"id": video_id}
    
    headers = {
        "x-rapidapi-key": rapid_key,
        "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        # This specific API returns the download URL under the "link" key
        if data.get("link"):
            return data.get("link"), None
        elif data.get("message"):
            return None, f"API Error: {data.get('message')}"
        else:
            return None, "Failed to generate download link."
            
    except Exception as e:
        return None, f"Network Error: {str(e)}"

# --- 3. Backend: Official YouTube API for Searching ---
def search_youtube_official(query):
    try:
        api_key = st.secrets["YOUTUBE_API_KEY"]
    except KeyError:
        st.error("API Key missing! Please add YOUTUBE_API_KEY to Streamlit Secrets.")
        return []

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=5&key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'video_id': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['high']['url']
            })
        return videos
    except Exception:
        return []

# --- 4. UI: Header & Search Bar ---
st.markdown("<h2 class='main-header'>🎵 YouTube Lunjir Downloader</h2>", unsafe_allow_html=True)

search_query = st.text_input("Lunjir amen tok ik non:", placeholder="e.g., New karbi song")

if st.button("Search"):
    if search_query:
        with st.spinner("Searching official YouTube database..."):
            search_results = search_youtube_official(search_query)
            
            if search_results:
                st.session_state.search_results = search_results
            else:
                st.warning("No results found or API limit reached.")

# --- 5. UI: Display Search Results ---
if "search_results" in st.session_state:
    st.write("### Search Results:")
    
    for idx, video in enumerate(st.session_state.search_results):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(video['thumbnail'], use_container_width=True)
            
        with col2:
            st.write(f"**{video['title']}**")
            st.write(f"Channel: {video['channel']}")
            
            if st.button(f"Convert to MP3", key=f"convert_{idx}"):
                with st.spinner("Authorizing and converting via RapidAPI..."):
                    # We only pass the video_id now, not the full URL
                    audio_link, error_msg = download_audio_api(video['video_id'])
                    
                    if audio_link:
                        st.success("✅ Conversion Complete!")
                        # This creates a native button that links to the MP3 URL!
                        st.link_button("➡️ Download MP3", audio_link)
                    else:
                        st.error(f"Error: {error_msg}")
                        
        
        st.markdown("---")
        
