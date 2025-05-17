# Islamic Finance News Credibility Assessor

This project fetches news articles related to Islamic finance standards using the News API, then employs a Generative AI model (Google Gemini) to assess whether the main claims in each article are "Credible" or "Not Credible". The results, including the AI's reasoning, are displayed in an interactive web application built with Streamlit.

## Features

*   **Automated News Fetching:** Retrieves recent news articles based on predefined Islamic finance keywords.
*   **AI-Powered Credibility Assessment:** Uses Google's Gemini Pro model to analyze article content and provide a "Credible" or "Not Credible" label.
*   **Reasoning Transparency:** Displays the AI's justification for its credibility assessment.
*   **Interactive Web UI:** Built with Streamlit for easy interaction (fetching news, triggering assessments).
*   **Data Export:** Allows downloading the assessed articles (including credibility labels and reasoning) as a JSON file.
*   **Standalone Script:** `main.py` can be run independently to fetch and assess articles, saving results to `articles.json`.

## How It Works

The application flow involves several steps:

1.  **API Key Configuration:** The user must provide their own API keys for News API (to fetch news) and Google AI Studio (for the Gemini Pro model) in a `.env` file.
2.  **News Fetching (Streamlit UI / `main.py`):**
    *   The `get_islamic_finance_news()` function in `main.py` queries the News API for articles matching specific keywords related to Islamic finance (e.g., AAOIFI, IFSB, Sukuk, Takaful).
    *   In the Streamlit app, clicking "Fetch Islamic Finance News" triggers this function.
3.  **Credibility Assessment (Streamlit UI / `main.py`):**
    *   The `NewsValidityAgent.py` class is responsible for interacting with the Gemini API.
    *   For each fetched article, the `create_credibility_prompt()` method constructs a detailed prompt. This prompt includes the article's title, source, author, description, and content snippet.
    *   The prompt instructs the Gemini model to act as a Fact-Checking Analyst and return a "Credible" or "Not Credible" assessment along with a brief reasoning, strictly following a specified output format.
    *   The `get_gemini_accuracy_response()` method sends this prompt to the Gemini API.
    *   The `parse_credibility_response()` method parses the AI's text response to extract the "Credibility" label and the reasoning.
    *   In the Streamlit app, clicking "Assess Article Credibility with AI" triggers this process for all fetched articles.
4.  **Displaying Results (Streamlit UI):**
    *   Fetched articles are displayed in expandable sections.
    *   After assessment, each article's section is updated to show:
        *   The AI's credibility label ("Credible" in green, "Not Credible" in red, or error states).
        *   The AI's reasoning.
5.  **Data Storage/Export:**
    *   When `main.py` is run directly, it saves the fetched and assessed articles to `articles.json`.
    *   The Streamlit application provides a "Download Assessed Articles (JSON)" button to save the currently displayed data.

## Prerequisites

*   Python 3.8 or higher
*   pip (Python package installer)
*   A News API Key: [https://newsapi.org/](https://newsapi.org/)
*   A Google API Key enabled for the Gemini API (Generative Language API): [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

## Setup and Installation

1.  **Clone the Repository (or Create Project Directory):**
    ```bash
    # If you have it in a git repository:
    # git clone <repository-url>
    # cd <repository-name>

    # Otherwise, ensure all project files are in a single directory (e.g., "isdbi-challenge3").
    cd "isdbi-challenge3"
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Install the required Python packages using pip:
    ```bash
    pip install streamlit python-dotenv requests google-generativeai
    ```
    Alternatively, if a `requirements.txt` file is provided:
    ```bash
    # (First, ensure requirements.txt exists with the above packages listed)
    # pip freeze > requirements.txt
    # pip install -r requirements.txt
    ```

## Configuration

The application requires API keys to function. These should be stored in a `.env` file in the root of the project directory (`/`).

1.  **Create a `.env` file** in the `isdbi-challenge3/` directory:
    ```
    isdbi-challenge3/
    ├── .env
    ├── NewsValidityAgent.py
    ├── articles.json
    ├── main.py
    └── app.py
    ...
    ```

2.  **Add your API keys to the `.env` file:**
    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    NEWS_API_KEY="YOUR_NEWS_API_KEY"
    ```
    Replace `"YOUR_GOOGLE_GEMINI_API_KEY"` and `"YOUR_NEWS_API_KEY"` with your actual keys.

    **Important:** Do NOT commit the `.env` file to version control if you are using Git, as it contains sensitive credentials. Ensure `.env` is listed in your `.gitignore` file.

## Running the Application

There are two main ways to run the project:

1.  **Via the Streamlit Web Application (Recommended for UI):**
    This will start a local web server and open the application in your browser.
    ```bash
    streamlit run app.py
    ```
    Navigate through the UI to fetch news and assess their credibility.

2.  **As a Standalone Python Script (for batch processing):**
    This will run the fetching and assessment process directly in your terminal and save the results to `articles.json`.
    ```bash
    python main.py
    ```
    The output and progress will be printed to the console.

## Project Structure

```
    isdbi-challenge3/
    ├── .env # Stores API keys (create this manually)
    ├── NewsValidityAgent.py # Class for interacting with Gemini API for credibility assessment
    ├── articles.json # Stores fetched and assessed articles (populated by main.py or downloaded via Streamlit)
    ├── main.py # Core logic for fetching news and can run standalone assessment
    ├── app.py # The Streamlit web application interface
    ├── my_project_context.txt # (Likely for your development context with the AI assistant)
    ├── venv/ # Python virtual environment (if created)
    └── pycache/ # Python bytecode cache
```

## File Descriptions

*   **`.env`**: Stores sensitive API keys for News API and Google Gemini.
*   **`NewsValidityAgent.py`**: Contains the `NewsValidityAgent` class, which handles the construction of prompts for the Gemini API, makes API calls, and parses the responses to determine credibility and reasoning.
*   **`articles.json`**: A JSON file where fetched articles and their credibility assessments are stored. This file is primarily written to when `main.py` is run directly or when results are downloaded from the Streamlit app.
*   **`main.py`**:
    *   Defines the `get_islamic_finance_news()` function to fetch articles from News API.
    *   The `if __name__ == "__main__":` block allows this script to be run directly from the command line to perform a full fetch and assessment cycle, saving results to `articles.json`.
*   **`app.py`**: Implements the user interface using Streamlit. It allows users to trigger news fetching, initiate AI-powered credibility assessments, and view the results interactively.

## Troubleshooting / Important Notes

*   **API Key Errors:** Ensure your API keys in `.env` are correct and have the necessary permissions/quotas.
    *   News API: Check for correct key and that your plan allows for the queries.
    *   Google Gemini API: Ensure the "Generative Language API" is enabled for your project in Google Cloud Console (or that your API key from AI Studio is active).
*   **Gemini Response Parsing:** The agent relies on Gemini to return responses in a specific format. If Gemini deviates significantly, parsing might fail. The prompt in `NewsValidityAgent.py` is designed to minimize this, but adjustments might be needed if issues arise. The agent attempts to handle common error responses from Gemini.
*   **Rate Limits:** Both News API and Gemini API have rate limits. If you process many articles very quickly, you might encounter temporary blocks. The `NewsValidityAgent` does not currently implement explicit rate limit handling (e.g., exponential backoff), but this could be added.
*   **Content Snippet Quality:** The quality of the "Content Snippet" from News API can vary. Sometimes it's limited or truncated, which might affect the AI's assessment accuracy.
*   **Cost:** Be mindful of potential costs associated with using the News API (depending on your plan) and the Google Gemini API (which has a free tier but charges for usage beyond that).

## Future Enhancements

*   Allow users to input custom search queries for news articles via the Streamlit UI.
*   Implement more robust error handling and retry mechanisms for API calls.
*   Add caching for News API responses to avoid re-fetching identical data rapidly.
*   Improve the UI/UX, perhaps with options to sort or filter articles.
*   Option to analyze a single URL provided by the user.
*   More sophisticated analysis of source reputation.