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
                # Preserve any existing indentation while wrapping in span
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    space_str = "&nbsp;" * leading_spaces
                    formatted_line = f"{space_str}{line.lstrip()}"
                else:
                    formatted_line = line
                formatted_lines.append(f'<span class="poem-line">{formatted_line}</span>')
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
            /* Reset and base styles */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: Georgia, 'Times New Roman', Times, serif;
                line-height: 1.6;
                color: #374151;
                max-width: 650px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8fafc;
            }

            /* Typography */
            h1 {
                color: #1e40af;
                font-size: 2rem;
                text-align: center;
                margin-bottom: 2rem;
                padding: 1rem;
                border-bottom: 3px double #1e40af;
                letter-spacing: 0.05em;
            }

            h2 {
                color: #1e3a8a;
                font-size: 1.5rem;
                margin: 2.5rem 0 1.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #bfdbfe;
            }

            h3 {
                color: #2563eb;
                font-size: 1.25rem;
                margin: 2rem 0 1rem;
                font-weight: 600;
            }

            p {
                margin-bottom: 1.2rem;
                font-size: 1.1rem;
            }

            /* Poem styling */
            .poem-container {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                margin: 2rem 0;
                overflow: hidden;
            }

            .poem-header {
                background: #f3f4f6;
                padding: 1rem;
                border-bottom: 1px solid #e5e7eb;
            }

            .poem-content {
                padding: 2rem;
                font-family: 'Crimson Text', Georgia, serif;
                line-height: 1.8;
                white-space: pre-wrap;
                font-size: 1.15rem;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            
            .poem-line {
                display: block;
                white-space: nowrap;
                min-width: min-content;
                padding-left: 2rem;
                text-indent: -2rem;
            }

            /* Analysis section */
            .analysis-section {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 1.5rem;
                margin: 2rem 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }

            .analysis-heading {
                color: #1e40af;
                font-size: 1.3rem;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #bfdbfe;
            }

            .analysis-content {
                padding: 0 1rem;
            }

            /* Quote styling */
            .poem-quote {
                margin: 1.5rem 0;
                padding: 1rem 1.5rem;
                border-left: 4px solid #3b82f6;
                background: #f8fafc;
                font-style: italic;
                color: #4b5563;
            }

            /* Writing prompt section */
            .writing-prompt {
                background: #dbeafe;
                border-radius: 8px;
                padding: 2rem;
                margin: 3rem 0;
                border: 1px solid #93c5fd;
            }

            .writing-prompt h2 {
                color: #1e40af;
                border: none;
                margin-top: 0;
            }

            .prompt-details {
                background: white;
                padding: 1.5rem;
                border-radius: 6px;
                margin-top: 1rem;
            }

            /* Responsive design */
            @media (max-width: 640px) {
                body {
                    padding: 16px;
                }

                h1 {
                    font-size: 1.75rem;
                }

                h2 {
                    font-size: 1.35rem;
                }

                .poem-content {
                    padding: 1.5rem;
                    font-size: 1rem;
                }

                .analysis-section {
                    padding: 1rem;
                }

                .poem-quote {
                    margin: 1rem 0;
                    padding: 0.75rem 1rem;
                }
            }

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                body {
                    background-color: #0f172a;
                    color: #e2e8f0;
                }

                .poem-container,
                .analysis-section {
                    background: #1e293b;
                    border-color: #334155;
                }

                .poem-header {
                    background: #334155;
                    border-color: #475569;
                }

                .poem-quote {
                    background: #1e293b;
                    color: #cbd5e1;
                }

                h1 {
                    color: #60a5fa;
                    border-bottom-color: #60a5fa;
                }

                h2 {
                    color: #93c5fd;
                    border-bottom-color: #1e40af;
                }

                h3, .analysis-heading {
                    color: #93c5fd;
                }

                .writing-prompt {
                    background: #1e3a8a;
                    border-color: #3b82f6;
                }

                .prompt-details {
                    background: #1e293b;
                }
            }
        </style>
        """

        email_parts = [css_styles]
        current_date = datetime.now().strftime("%B %d, %Y")
        email_parts.append(f"<h1>Daily Poetry Collection - {current_date}</h1>")

        for i, poem in enumerate(poems, 1):
            analysis = self.get_poem_analysis(poem)
            # Format the poem section
            poem_section = f"""
                <div class="poem-container">
                    <div class="poem-header">
                        <h2>{poem['title']} by {poem['author']}</h2>
                    </div>
                    <div class="poem-content">
                        {self.format_poem_text(poem['lines'])}
                    </div>
                </div>
            """
            
            # Split analysis into sections and format them
            analysis_sections = analysis.split("\n\n")
            formatted_analysis = '<div class="analysis-section">'
            
            for section in analysis_sections:
                if section.strip():
                    if ":" in section:
                        title, content = section.split(":", 1)
                        formatted_analysis += f"""
                            <div class="analysis-content">
                                <h3 class="analysis-heading">{title.strip()}</h3>
                                <div class="analysis-text">{content.strip()}</div>
                            </div>
                        """
                    else:
                        formatted_analysis += f'<div class="analysis-text">{section.strip()}</div>'
            
            formatted_analysis += '</div>'
            
            email_parts.extend([poem_section, formatted_analysis])

        # Add writing prompt
        prompt = self.get_writing_prompt()
        writing_prompt = f"""
        <div class='writing-prompt'>
            <h2>🖋️ Today's Writing Challenge</h2>
            <div class="prompt-details">
                <p><strong>Form:</strong> {prompt['form']}</p>
                <p><strong>Structure:</strong> {prompt['structure']}</p>
                <p><strong>Rhyme Scheme:</strong> {prompt['rhyme_scheme']}</p>
                <div class="poem-quote">
                    <p><em>Prompt:</em> {prompt['prompt']}</p>
                </div>
                <p>✨ Try writing your own poem following these guidelines. Take inspiration from today's readings and remember that working within formal constraints can help develop your poetic voice!</p>
            </div>
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
