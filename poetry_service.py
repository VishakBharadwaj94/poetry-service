import os
import requests
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [Previous PoetryDB class code remains exactly the same]

class PoetryDB:
    """Handles interactions with the PoetryDB API."""
    BASE_URL = "https://poetrydb.org"
    
    @staticmethod
    def get_authors() -> List[str]:
        try:
            response = requests.get(f"{PoetryDB.BASE_URL}/author")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched {len(data['authors'])} authors")
                return data['authors']
            else:
                logger.error(f"Failed to fetch authors. Status code: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching authors: {str(e)}")
            return []

    @staticmethod
    def get_poems_by_author(author: str) -> List[Dict[str, Any]]:
        try:
            encoded_author = requests.utils.quote(author)
            response = requests.get(f"{PoetryDB.BASE_URL}/author/{encoded_author}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both list and dict responses
                if isinstance(data, list):
                    poems = data
                elif isinstance(data, dict):
                    # If it's a dict with numbered keys, convert to list
                    poems = [v for k, v in data.items() if isinstance(k, (int, str)) and isinstance(v, dict)]
                else:
                    logger.error(f"Unexpected response format for {author}")
                    return []
                
                logger.info(f"Successfully fetched {len(poems)} poems for {author}")
                return poems
            else:
                logger.error(f"Failed to fetch poems for {author}. Status code: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching poems for {author}: {str(e)}")
            return []

class PoetryService:
    def __init__(self):
        """Initialize using environment variables for configuration."""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.environ['GMAIL_ADDRESS']
        self.password = os.environ['GMAIL_APP_PASSWORD']
        self.openai_api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(api_key=self.openai_api_key)
        self.poetry_db = PoetryDB()
        
        # Preferred authors - can be customized
        self.preferred_authors = [
            "Emily Dickinson",
            "Robert Frost",
            "William Shakespeare",
            "Walt Whitman",
            "William Wordsworth"
        ]

    def get_poem_analysis(self, poem: Dict[str, Any]) -> str:
        """Get poem analysis from GPT."""
        try:
            prompt = f"""
            Please analyze this poem:

            Title: {poem['title']}
            Author: {poem['author']}

            {chr(10).join(poem['lines'])}

            Provide a thorough analysis including:
            1. Form and structure
            2. Meter and rhyme scheme
            3. Key themes and imagery
            4. Literary devices used
            5. Historical or biographical context if relevant

            Format the analysis in a clear, readable way.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting poem analysis: {str(e)}")
            return "Analysis unavailable at this time."

    def select_daily_poems(self) -> List[Dict[str, Any]]:
        """Select 3 random poems for today."""
        selected_poems = []
        available_authors = self.preferred_authors.copy()
        random.shuffle(available_authors)
        
        logger.info(f"Attempting to fetch poems from authors: {available_authors}")
        
        for author in available_authors:
            poems = self.poetry_db.get_poems_by_author(author)
            
            if poems:
                logger.info(f"Found {len(poems)} poems for {author}")
                try:
                    selected_poem = random.choice(poems)
                    selected_poems.append(selected_poem)
                    logger.info(f"Selected poem '{selected_poem.get('title', 'Untitled')}' by {author}")
                except Exception as e:
                    logger.error(f"Error selecting poem for {author}: {str(e)}")
                    continue
            
            if len(selected_poems) == 3:
                break
        
        logger.info(f"Successfully selected {len(selected_poems)} poems")
        return selected_poems

    def send_poetry_email(self):
        """Send today's poetry email."""
        try:
            poems = self.select_daily_poems()
            
            if not poems:
                logger.error("No poems could be retrieved")
                return
            
            msg = MIMEMultipart()
            msg['Subject'] = f'Your Daily Poetry Analysis - {datetime.now().strftime("%Y-%m-%d")}'
            msg['From'] = self.email.strip()  # Remove any whitespace
            msg['To'] = "vishak.svec@gmail.com".strip()
            
            email_content = []
            for poem in poems:
                analysis = self.get_poem_analysis(poem)
                
                poem_section = f"""
                {'='*50}
                
                Poet: {poem['author']}
                Title: {poem['title']}
                
                {chr(10).join(poem['lines'])}
                
                Analysis:
                {analysis}
                
                {'='*50}
                """
                email_content.append(poem_section)
            
            # Clean the content and ensure proper encoding
            clean_content = '\n'.join(email_content).encode('ascii', 'ignore').decode('ascii')
            msg.attach(MIMEText(clean_content, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                logger.info("Successfully sent poetry email")
                
        except Exception as e:
            logger.error(f"Error sending poetry email: {str(e)}")
            raise

def main():
    service = PoetryService()
    service.send_poetry_email()

if __name__ == "__main__":
    main()
