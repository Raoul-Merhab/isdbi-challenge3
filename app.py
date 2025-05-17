# streamlit_app.py

import streamlit as st
import os
import json
from dotenv import load_dotenv

# Import your existing modules
from NewsValidityAgent import NewsValidityAgent # Ensure this imports the updated agent
from main import get_islamic_finance_news 

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="News Credibility Assessor",
    page_icon="⚖️",
    layout="wide"
)

# --- API Key Initialization ---
gemini_api_key = os.getenv("GOOGLE_API_KEY")
news_api_key_env = os.getenv("NEWS_API_KEY")

# --- Initialize Session State ---
if 'articles' not in st.session_state:
    st.session_state.articles = []  # Will store full article data from News API
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
if 'processing_validation' not in st.session_state: 
    st.session_state.processing_validation = False


# --- App Title & Description ---
st.title("⚖️ Islamic Finance News Credibility Assessor")
st.markdown("""
    This application fetches news articles related to Islamic finance standards
    and uses a Generative AI model (Gemini) to assess if their claims are "Credible" or "Not Credible".
    
    **Instructions:**
    1. Ensure your `GOOGLE_API_KEY` and `NEWS_API_KEY` are set in the `.env` file.
    2. Click "Fetch Islamic Finance News" in the sidebar.
    3. Once articles are fetched, click "Assess Article Credibility with AI".
""")

# --- API Key Checks ---
if not news_api_key_env:
    st.error("⚠️ News API Key not found. Please set `NEWS_API_KEY` in your .env file.")
if not gemini_api_key:
    st.warning("⚠️ Google API Key not found. Please set `GOOGLE_API_KEY` in your .env file. Credibility assessment will not be possible.")


# --- Sidebar for Actions ---
st.sidebar.header("Actions")

if st.sidebar.button("Fetch Islamic Finance News", disabled=not news_api_key_env):
    if not news_api_key_env:
        st.sidebar.error("News API Key is missing. Cannot fetch news.")
    else:
        st.session_state.articles = [] 
        st.session_state.error_message = ""
        with st.spinner("Fetching news articles..."):
            try:
                news_data = get_islamic_finance_news() 
                
                if news_data.get("status") == "ok":
                    fetched_articles = news_data.get("articles", [])
                    if fetched_articles:
                        st.session_state.articles = fetched_articles
                        st.sidebar.success(f"Successfully fetched {len(fetched_articles)} articles!")
                    else:
                        st.session_state.error_message = "No articles found for the query."
                        st.sidebar.warning("No articles found.")
                else:
                    error_msg = news_data.get("message", "Unknown error from News API.")
                    st.session_state.error_message = f"News API Error: {error_msg}"
                    st.sidebar.error(f"News API Error: {error_msg}")
            except Exception as e:
                st.session_state.error_message = f"Error during news fetching: {str(e)}"
                st.sidebar.error(f"Fetching Error: {str(e)}")
        st.rerun() 

if st.session_state.articles:
    if st.sidebar.button("Assess Article Credibility with AI", disabled=not gemini_api_key or st.session_state.processing_validation):
        if not gemini_api_key:
            st.sidebar.error("Google API Key is missing. Cannot assess credibility.")
        else:
            st.session_state.error_message = ""
            st.session_state.processing_validation = True
            
            agent = NewsValidityAgent(api_key=gemini_api_key)
            articles_to_validate = st.session_state.articles

            for article in st.session_state.articles:
                article.pop('credibility_label', None)
                article.pop('credibility_reasoning', None) # Renamed from validity_reasoning

            status_message_area = st.sidebar.empty()
            progress_bar = st.sidebar.progress(0)
            
            total_articles = len(articles_to_validate)

            try:
                with st.spinner(f"Assessing credibility for {total_articles} articles..."):
                    # agent.check_news_claim now returns list of dicts with 'credibility_label' and 'reasoning'
                    validation_responses = agent.check_news_claim(articles_to_validate)

                    for i, val_info in enumerate(validation_responses):
                        article_title_to_match = val_info.get("original_title_for_matching", val_info.get("title"))
                        
                        matched_article = next(
                            (art for art in st.session_state.articles if art['title'] == article_title_to_match), None
                        )

                        if matched_article:
                            matched_article['credibility_label'] = val_info.get('credibility_label')
                            matched_article['credibility_reasoning'] = val_info.get('reasoning', 'No reasoning provided.')
                        else:
                            st.warning(f"Could not match validation result for title: {article_title_to_match}")
                        
                        progress_bar.progress((i + 1) / total_articles)
                        status_message_area.info(f"Assessed {(i + 1)}/{total_articles} articles...")

                status_message_area.success("Credibility assessment complete!")
                st.sidebar.success("All articles processed!")

            except Exception as e:
                st.session_state.error_message = f"Error during AI assessment: {str(e)}"
                st.sidebar.error(f"AI Assessment Error: {str(e)}")
                status_message_area.error("Assessment failed.")
            finally:
                st.session_state.processing_validation = False
                progress_bar.empty() 
                st.rerun()

# Download button
if st.session_state.articles and any('credibility_label' in art for art in st.session_state.articles):
    try:
        articles_for_download = []
        for art_data in st.session_state.articles:
            # Ensure structure for download matches what you expect (e.g., 'credibility_label', 'credibility_reasoning')
            download_art = {
                "title": art_data.get("title"),
                "source": art_data.get("source"),
                "author": art_data.get("author"),
                "publishedAt": art_data.get("publishedAt"),
                "url": art_data.get("url"),
                "description": art_data.get("description"),
                "content": art_data.get("content"),
                "credibility_label": art_data.get("credibility_label", "Not Assessed"),
                "credibility_reasoning": art_data.get("credibility_reasoning", "N/A")
            }
            articles_for_download.append(download_art)

        articles_json_string = json.dumps(articles_for_download, indent=2, ensure_ascii=False)
        st.sidebar.download_button(
            label="Download Assessed Articles (JSON)",
            data=articles_json_string,
            file_name="assessed_articles.json",
            mime="application/json"
        )
    except Exception as e:
        st.sidebar.error(f"Error preparing download: {e}")


# --- Display Error Messages ---
if st.session_state.error_message:
    st.error(st.session_state.error_message)

# --- Display Fetched Articles (and Assessment Results) ---
if st.session_state.articles:
    st.header("Fetched Articles")
    st.markdown(f"Displaying **{len(st.session_state.articles)}** articles.")

    for i, article in enumerate(st.session_state.articles):
        expander_title_parts = []
        expander_title_parts.append(article.get('title', f'Untitled Article {i+1}'))
        
        if 'credibility_label' in article and article['credibility_label'] not in [None, "Parsing Failed", "Error"]:
            expander_title_parts.append(f"(Assessment: {article['credibility_label']})")
        elif st.session_state.processing_validation: 
             expander_title_parts.append("(Assessing...)")
        
        source_name = article.get('source', {}).get('name', 'N/A')
        expander_title_parts.append(f"- *Source: {source_name}*")
        
        expander_title = " ".join(expander_title_parts)

        with st.expander(expander_title):
            st.markdown(f"**Published At:** {article.get('publishedAt', 'N/A')}")
            st.markdown(f"**Author:** {article.get('author', 'N/A')}")
            
            description = article.get('description')
            if description: 
                st.markdown(f"**Description:** {description}")
            
            content_snippet = article.get('content') 
            if content_snippet: 
                st.markdown(f"**Content Snippet:** {content_snippet}")

            if article.get('url'):
                st.markdown(f"[Read full article]({article.get('url')})", unsafe_allow_html=True)
            
            if 'credibility_label' in article: 
                st.markdown(f"---") 
                st.markdown(f"**AI Credibility Assessment:**")
                
                label = article['credibility_label']
                reasoning = article.get('credibility_reasoning', 'Reasoning not available.') 
                
                label_display = "N/A"
                color = "grey"

                if label == "Credible":
                    label_display = "Credible"
                    color = "green"
                elif label == "Not Credible":
                    label_display = "Not Credible"
                    color = "red"
                elif label in ["Error", "Parsing Failed"]:
                    label_display = f"Assessment Error ({label})"
                    color = "orange"
                elif label is None: # Should ideally be caught by the above or default to "Not Assessed"
                    label_display = "Not Assessed"
                else: # Any other unexpected label
                    label_display = label
                    color = "blue"


                st.markdown(f"**Assessment:** <font color='{color}'><b>{label_display}</b></font>", unsafe_allow_html=True)
                st.markdown(f"**Reasoning:** {reasoning}")
            
            elif not st.session_state.processing_validation: 
                st.markdown("_(Awaiting assessment or assessment data not available)_")

elif not st.session_state.error_message: 
    st.info("No articles fetched yet. Click 'Fetch Islamic Finance News' in the sidebar.")

# --- Footer ---
st.markdown("---")
st.markdown("App by AI Insights Co. | Powered by NewsAPI and Google Gemini")

if __name__ == '__main__':
    pass