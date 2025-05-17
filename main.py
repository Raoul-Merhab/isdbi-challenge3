import requests
import json
import os
from NewsValidityAgent import NewsValidityAgent # Ensure this imports the updated agent
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv("GOOGLE_API_KEY")

# News API configuration
news_url = "https://newsapi.org/v2/everything"
news_api_key = os.getenv("NEWS_API_KEY")

def get_islamic_finance_news():
    """Fetch news articles related to Islamic finance standards"""
    params = {
        "q": (
            "AAOIFI OR IFSB OR 'Islamic finance' OR 'Shariah compliance' OR "
            "'Shariah board' OR 'Islamic banking standards' OR 'fatwa finance' OR "
            "'Islamic financial regulation' OR 'Islamic accounting' OR 'Sukuk' OR "
            "'Takaful' OR Murabaha OR Musharaka OR Mudaraba"
        ),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,  # Max results per call
        "apiKey": news_api_key,
    }

    try:
        response = requests.get(news_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return {"status": "error", "articles": [], "message": str(e)}


if __name__ == "__main__":
    if not news_api_key:
        print("NEWS_API_KEY not found in .env file. Exiting.")
    elif not gemini_api_key:
        print("GOOGLE_API_KEY not found in .env file. Cannot perform validation. Exiting.")
    else:
        print("Fetching articles...")
        crawler_result = get_islamic_finance_news()
        articles = crawler_result.get("articles", [])

        if not articles:
            print("No articles fetched or an error occurred during fetching.")
        else:
            print(f"Fetched {len(articles)} articles. Saving initial fetch to articles_fetched.json")
            with open("articles_fetched.json", "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print("Initializing NewsValidityAgent...")
            agent = NewsValidityAgent(gemini_api_key)
            
            print("Validating articles...")
            validated_articles_data = agent.check_news_claim(articles) # This now returns list of dicts with 'credibility_label'
            
            print("\nValidation Results:")
            for val_data in validated_articles_data:
                print(f"  Title: {val_data.get('title')}")
                print(f"  Credibility: {val_data.get('credibility_label')}")
                print(f"  Reasoning: {val_data.get('reasoning')}\n")

            # Merge validation results back into the original articles list
            # This ensures articles.json has all original data + validation
            articles_with_validation = []
            for original_article in articles:
                # Find the corresponding validation data
                # Using original_title_for_matching if available, otherwise title
                match_found = False
                for val_data in validated_articles_data:
                    if original_article.get("title") == val_data.get("original_title_for_matching"):
                        # Create a new dictionary to avoid modifying original_article in place if it's referenced elsewhere
                        updated_article = original_article.copy()
                        updated_article['credibility_label'] = val_data.get('credibility_label')
                        updated_article['credibility_reasoning'] = val_data.get('reasoning') # Using 'credibility_reasoning'
                        articles_with_validation.append(updated_article)
                        match_found = True
                        break
                if not match_found: # If no match (shouldn't happen if titles are consistent)
                    articles_with_validation.append(original_article.copy())


            print(f"Saving articles with credibility assessment to articles.json")
            with open("articles.json", "w", encoding="utf-8") as f:
                json.dump(articles_with_validation, f, ensure_ascii=False, indent=2)
            print("Process complete. Check articles.json.")