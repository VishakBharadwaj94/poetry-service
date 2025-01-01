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
                
                if isinstance(data, list):
                    poems = data
                elif isinstance(data, dict):
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
        self.email = os.environ['GMAIL_ADDRESS'].strip().encode('ascii', 'ignore').decode('ascii')
        self.password = os.environ['GMAIL_APP_PASSWORD'].strip().encode('ascii', 'ignore').decode('ascii')
        self.openai_api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(api_key=self.openai_api_key)
        self.poetry_db = PoetryDB()

        # List of poets (randomly selected later)
        self.all_authors = [
            "Edgar Allan Poe", "Elizabeth Barrett Browning", "Emily Bronte",
            "Emily Dickinson", "Christina Rossetti", "Matthew Arnold",
            "Robert Browning", "Alfred, Lord Tennyson", "Percy Bysshe Shelley",
            "William Wordsworth", "Wilfred Owen", "Rupert Brooke",
            "Joyce Kilmer", "Paul Laurence Dunbar", "Edward Thomas"
        ]

    def get_poem_analysis(self, poem: Dict[str, Any]) -> str:
        """Get poem analysis from GPT."""
        try:
            prompt = f"""
            Please analyze this poem:

            Title: {poem['title']}
            Author: {poem['author']}

            {chr(10).join(poem['lines'])}

            Provide a thorough analysis covering:
            <h3>1. Form and Structure</h3>
            - Discuss meter, rhyme scheme, and stanza organization.

            <h3>2. Key Themes and Imagery</h3>
            - Highlight recurring motifs and symbolic imagery.

            <h3>3. Literary Devices</h3>
            - Explain figures of speech such as metaphors, similes, and personification.

            <h3>4. Historical and Biographical Context</h3>
            - Provide background influences, author’s life events, and interpretations.

            <h3>5. Metaphorical and Thematic Exploration</h3>
            - Delve deeper into metaphors, allusions, and themes connected to the poet’s broader work.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting poem analysis: {str(e)}")
            return "Analysis unavailable at this time."

    def format_poem_text(self, lines: List[str]) -> str:
        """Format poem with proper indentation and spacing."""
        formatted_lines = []
        for line in lines:
            if line.strip():
                formatted_lines.append(f"&nbsp;&nbsp;&nbsp;&nbsp;{line}")
            else:
                formatted_lines.append("<br>")
        return "<br>".join(formatted_lines)

    def select_daily_poems(self) -> List[Dict[str, Any]]:
        """Select 3 random poems for today."""
        selected_poems = []
        available_authors = random.sample(self.all_authors, 3)

        logger.info(f"Selected random authors: {available_authors}")

        for author in available_authors:
            poems = self.poetry_db.get_poems_by_author(author)
            
            if poems:
                try:
                    selected_poem = random.choice(poems)
                    selected_poems.append(selected_poem)
                except Exception as e:
                    logger.error(f"Error selecting poem for {author}: {str(e)}")
                    continue

            if len(selected_poems) == 3:
                break

        return selected_poems

    def create_email_content(self, poems: List[Dict[str, Any]]) -> str:
        """Create beautifully formatted email content."""
        email_parts = []
        current_date = datetime.now().strftime("%B %d, %Y")
        email_parts.append(f"<h1>Daily Poetry Collection - {current_date}</h1>")

        for i, poem in enumerate(poems, 1):
            analysis = self.get_poem_analysis(poem)
            email_parts.append(f"<h2>{poem['title']} by {poem['author']}</h2><pre>{self.format_poem_text(poem['lines'])}</pre><p><strong>Analysis:</strong></p>{analysis}")

        return "<br><br>".join(email_parts)

    def send_poetry_email(self):
        """Send today's poetry email."""
        poems = self.select_daily_poems()
        if not poems:
            return

        msg = MIMEMultipart()
        msg['Subject'] = f'Your Daily Poetry Collection - {datetime.now().strftime("%B %d")}'
        msg['From'] = self.email
        msg['To'] = self.email
        msg.attach(MIMEText(self.create_email_content(poems), 'html'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)

if __name__ == "__main__":
    PoetryService().send_poetry_email()
