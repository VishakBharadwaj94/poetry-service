import os
import requests
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any

class PoetryDB:
    """Handles interactions with the PoetryDB API."""
    BASE_URL = "https://poetrydb.org"
    
    @staticmethod
    def get_authors() -> List[str]:
        response = requests.get(f"{PoetryDB.BASE_URL}/author")
        return response.json()['authors']

    @staticmethod
    def get_poems_by_author(author: str) -> List[Dict[str, Any]]:
        response = requests.get(f"{PoetryDB.BASE_URL}/author/{author}")
        return response.json()

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

    def select_daily_poems(self) -> List[Dict[str, Any]]:
        """Select 3 random poems for today."""
        import random
        
        selected_poems = []
        authors = self.preferred_authors.copy()
        random.shuffle(authors)
        
        for author in authors:
            poems = self.poetry_db.get_poems_by_author(author)
            if poems:
                selected_poem = random.choice(poems)
                selected_poems.append(selected_poem)
            
            if len(selected_poems) == 3:
                break
                
        return selected_poems

    def send_poetry_email(self):
        """Send today's poetry email."""
        poems = self.select_daily_poems()
        
        msg = MIMEMultipart()
        msg['Subject'] = f'Your Daily Poetry Analysis - {datetime.now().strftime("%Y-%m-%d")}'
        msg['From'] = self.email
        msg['To'] = "vishak.svec@gmail.com"
        
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
        
        msg.attach(MIMEText('\n'.join(email_content), 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)

def main():
    service = PoetryService()
    service.send_poetry_email()

if __name__ == "__main__":
    main()
