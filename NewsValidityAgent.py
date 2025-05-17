import google.generativeai as genai
import re

class NewsValidityAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
    
    def create_credibility_prompt(self, article_data): # Renamed method
        """
        Creates a prompt for Gemini to provide a "Credible" or "Not Credible" assessment and reasoning.
        """
        title = article_data["title"] if article_data["title"] else "N/A"
        description = article_data["description"] if article_data["description"] else "N/A"
        content_snippet = article_data["content"] if article_data["content"] else "N/A"
        source_name = article_data["source"]["name"] if article_data["source"]["name"] else "N/A"
        author = article_data["author"] if article_data["author"] else "N/A"
        published_at = article_data["publishedAt"] if article_data["publishedAt"] else "N/A"

        prompt = f"""
        You are a Fact-Checking Analyst AI. Your task is to evaluate the provided news article details and determine if its main factual claims are "Credible" or "Not Credible", along with a brief justification.

        Article Information:
        - Title: "{title}"
        - Source Name (News Outlet): "{source_name}"
        - Author/Publisher of Report (cited in article, or journalist): "{author}"
        - Publication Date of News Item: "{published_at}"
        - Description Snippet: "{description}"
        - Content Snippet: "{content_snippet}"

        Instructions for your analysis (consider these points before giving the assessment):
        1.  **Key Claims:** Identify the main factual claims (e.g., market size "$X Trillion by YYYY", "Z% CAGR", specific events, attributions).
        2.  **News Outlet ({source_name}):** Assess its nature. Is it a primary news source (e.g., Reuters, Associated Press), a press release distributor (e.g., GlobeNewswire, PR Newswire), an aggregator, a blog? This affects how the information should be viewed.
        3.  **Author/Original Source ({author}):** Assess its likely standing. Is it a known market research firm, an established journalist, a company making an announcement, an academic body, an individual, etc.?
        4.  **Nature of Claims:** Are these established facts, company announcements, or projections/forecasts? Projections inherently carry uncertainty. A claim being a projection doesn't automatically make it "Not Credible" but its basis should be considered.
        5.  **Red Flags/Context:**
            - Is the news outlet primarily a distributor of press releases? This means the content is likely paid for by the "author" and not independently vetted by the outlet. This leans towards "Not Credible" for independent factual claims unless the original source is highly reputable.
            - Is the language overly promotional or biased?
            - Are there any obvious contradictions or unsourced significant claims?

        **Output Requirement:**
        Based on your internal analysis of the above, provide your response *strictly* in the following format:

        Estimated Credibility: [Credible/Not Credible]
        Reasoning: [Your brief explanation, typically 2-4 sentences, justifying the assessment based on your analysis of source, author, and claim nature.]

        Example 1:
        Estimated Credibility: Credible
        Reasoning: The article reports on an official announcement from a regulatory body (IFSB), published by a reputable news agency (Reuters). The claims are factual statements about new standards being released.

        Example 2:
        Estimated Credibility: Not Credible
        Reasoning: The claims are bold market projections from an unknown research firm, distributed via a press release service (GlobeNewswire). The language is highly promotional, and no independent verification is provided by the news outlet.

        Do not add any other text before "Estimated Credibility:" or after the reasoning.
        Only use "Credible" or "Not Credible" as the assessment.
        """
        return prompt

    def get_gemini_accuracy_response(self, prompt_text): # Name kept for now, but it's now 'credibility'
        """
        Sends the prompt to Gemini and gets the response.
        """
        model = genai.GenerativeModel('gemini-2.0-flash') # Using gemini-pro for potentially better nuanced reasoning
        try:
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            error_message = f"An error occurred while contacting Gemini: {str(e)}"
            # Basic error handling; you might want to log more details or check specific error types
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback.block_reason:
                error_message += f" | Block Reason: {e.response.prompt_feedback.block_reason}"
            elif hasattr(e, 'message') and "quota" in e.message.lower():
                error_message += " | This might be a rate limit or quota issue. Please check your API usage."
            return error_message


    def parse_credibility_response(self, response_text): # Renamed method
        """
        Parses the "Credible"/"Not Credible" label and reasoning from Gemini's response.
        Returns a dictionary: {"label": str, "reasoning": str} or defaults if parsing fails.
        """
        label = None
        reasoning = "Could not parse reasoning from Gemini's response." # Default

        # Regex to capture "Credible" or "Not Credible"
        label_match = re.search(r"Estimated Credibility:\s*(Credible|Not Credible)", response_text, re.IGNORECASE)
        if label_match:
            label = label_match.group(1).capitalize() # Ensure consistent capitalization

        reasoning_match = re.search(r"Reasoning:\s*(.*)", response_text, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        # Handle specific error messages from Gemini API
        elif "An error occurred" in response_text or "Content blocked" in response_text or "quota" in response_text.lower():
            reasoning = response_text 
            label = "Error" # Special label for errors

        elif label is None and not reasoning_match: # If both failed to parse
            reasoning = f"Failed to parse the expected format from AI. Raw response: {response_text}"
            label = "Parsing Failed"

        return {"label": label, "reasoning": reasoning}


    def check_news_claim(self, article_news):
        articles_list = article_news
        all_results_detailed = []

        if not articles_list:
            print("No articles found in the JSON or JSON was invalid.") # This print is for direct use, not Streamlit
            return [] 
        else:
            # This print is also for direct use, Streamlit will have its own progress indication
            # print(f"--- Processing {len(articles_list)} Articles ---") 
            for article_data in articles_list:
                article_title = article_data.get("title", "N/A") # Use .get for safety

                prompt = self.create_credibility_prompt(article_data) # Use new prompt method

                raw_gemini_response = self.get_gemini_accuracy_response(prompt)
                parsed_response = self.parse_credibility_response(raw_gemini_response) # Use new parsing method
                
                all_results_detailed.append({
                    "original_title_for_matching": article_data.get("title"), # Ensure this is the exact original title
                    "title": article_title,
                    "credibility_label": parsed_response.get("label"), # New field
                    "reasoning": parsed_response.get("reasoning")
                })
            return all_results_detailed