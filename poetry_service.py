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

        self.all_authors = [
            "Edgar Allan Poe", "Elizabeth Barrett Browning", "Emily Bronte",
            "Emily Dickinson", "Christina Rossetti", "Matthew Arnold",
            "Robert Browning", "Alfred, Lord Tennyson", "Percy Bysshe Shelley",
            "William Wordsworth", "Wilfred Owen", "Rupert Brooke",
            "Joyce Kilmer", "Paul Laurence Dunbar", "Edward Thomas"
        ]

        # Add poetic forms for writing prompts
        self.poetic_forms = [
            {
                "name": "Sonnet",
                "structure": "14 lines, typically in iambic pentameter",
                "rhyme_scheme": "Various schemes including Shakespearean (ABAB CDCD EFEF GG) or Petrarchan (ABBAABBA CDECDE)",
                "example_prompt": "Write about a transformative moment in nature"
            },
            {
                "name": "Haiku",
                "structure": "3 lines with syllables 5-7-5",
                "rhyme_scheme": "No specific rhyme scheme",
                "example_prompt": "Capture a fleeting seasonal moment"
            },
            {
                "name": "Villanelle",
                "structure": "19 lines with repeating refrains",
                "rhyme_scheme": "ABA ABA ABA ABA ABA ABAA",
                "example_prompt": "Express an obsessive thought or memory"
            },
            {
                "name": "Ballad",
                "structure": "Quatrains with alternating 4-beat and 3-beat lines",
                "rhyme_scheme": "ABCB",
                "example_prompt": "Tell a story of love or loss"
            }
        ]

    def get_poem_analysis(self, poem: Dict[str, Any]) -> str:
        """Get detailed poem analysis from GPT with specific line references."""
        try:
            prompt = f"""
            Analyze this poem with specific line references and detailed explanations:

            Title: {poem['title']}
            Author: {poem['author']}

            {chr(10).join(poem['lines'])}

            Provide a thorough analysis covering:
            1. Form and Structure
            - Examine the specific meter and rhythm, citing example lines
            - Explain the rhyme scheme with examples
            - Describe how stanza organization contributes to meaning

            2. Key Themes and Imagery
            - Quote specific lines that demonstrate important images
            - Show how imagery patterns develop throughout the poem
            - Connect imagery to broader themes

            3. Literary Devices
            - Quote and explain specific metaphors, similes, and other figures of speech
            - Show how these devices contribute to the poem's meaning
            - Identify sound devices (alliteration, assonance) with examples

            4. Historical and Personal Context
            - Connect the poem to specific events or experiences in the poet's life
            - Explain relevant historical or cultural references
            - Show how context illuminates meaning

            5. Deep Reading
            - Analyze how specific word choices create meaning
            - Explore ambiguities or multiple interpretations
            - Connect this poem to the poet's broader themes and style

            Please write in an engaging, accessible style while maintaining analytical depth.
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

    def get_writing_prompt(self) -> Dict[str, str]:
        """Generate a random writing prompt using poetic forms."""
        form = random.choice(self.poetic_forms)
        return {
            "form": form["name"],
            "structure": form["structure"],
            "rhyme_scheme": form["rhyme_scheme"],
            "prompt": form["example_prompt"]
        }

    def create_email_content(self, poems: List[Dict[str, Any]]) -> str:
        """Create beautifully formatted email content with responsive design."""
        css_styles = """
        <style>
            body {
                font-family: Georgia, 'Times New Roman', Times, serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            @media (max-width: 600px) {
                body {
                    padding: 15px;
                }
            }
            h1 {
                color: #2c5282;
                font-size: 28px;
                text-align: center;
                border-bottom: 2px solid #2c5282;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }
            h2 {
                color: #2d3748;
                font-size: 24px;
                margin-top: 40px;
                border-left: 4px solid #2c5282;
                padding-left: 15px;
            }
            .poem {
                background-color: #f7fafc;
                padding: 25px;
                border-radius: 8px;
                margin: 20px 0;
                font-family: 'Courier New', Courier, monospace;
                line-height: 1.8;
                white-space: pre-wrap;
            }
            .analysis {
                background-color: #fff;
                padding: 20px;
                border-left: 3px solid #4a5568;
                margin: 20px 0;
            }
            .analysis h3 {
                color: #4a5568;
                font-size: 20px;
                margin-top: 25px;
            }
            .quote {
                font-style: italic;
                color: #4a5568;
                padding: 10px 20px;
                border-left: 2px solid #718096;
                margin: 15px 0;
            }
            .writing-prompt {
                background-color: #ebf4ff;
                padding: 25px;
                border-radius: 8px;
                margin-top: 40px;
            }
            .writing-prompt h2 {
                color: #2c5282;
                border-left: none;
                margin-top: 0;
            }
            @media (prefers-color-scheme: dark) {
                body {
                    background-color: #1a202c;
                    color: #e2e8f0;
                }
                .poem {
                    background-color: #2d3748;
                    color: #e2e8f0;
                }
                .analysis {
                    background-color: #2d3748;
                    border-left-color: #4a5568;
                }
                .quote {
                    color: #a0aec0;
                }
                .writing-prompt {
                    background-color: #2a4365;
                    color: #e2e8f0;
                }
                h1, h2, .analysis h3 {
                    color: #90cdf4;
                }
            }
        </style>
        """

        email_parts = [css_styles]
        current_date = datetime.now().strftime("%B %d, %Y")
        email_parts.append(f"<h1>Daily Poetry Collection - {current_date}</h1>")

        for i, poem in enumerate(poems, 1):
            analysis = self.get_poem_analysis(poem)
            email_parts.extend([
                f"<h2>{poem['title']} by {poem['author']}</h2>",
                f"<div class='poem'>{self.format_poem_text(poem['lines'])}</div>",
                f"<div class='analysis'>{analysis}</div>"
            ])

        # Add writing prompt
        prompt = self.get_writing_prompt()
        writing_prompt = f"""
        <div class='writing-prompt'>
            <h2>Today's Writing Challenge</h2>
            <p><strong>Form:</strong> {prompt['form']}</p>
            <p><strong>Structure:</strong> {prompt['structure']}</p>
            <p><strong>Rhyme Scheme:</strong> {prompt['rhyme_scheme']}</p>
            <p><strong>Writing Prompt:</strong> {prompt['prompt']}</p>
            <p>Try writing your own poem following these guidelines. Remember that understanding form helps develop your poetic voice!</p>
        </div>
        """
        email_parts.append(writing_prompt)

        return "\n".join(email_parts)

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
