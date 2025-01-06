import os
import requests
from openai import OpenAI
from datetime import datetime
from typing import List, Dict, Any
import random
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoetryDB:
    """Handles interactions with the PoetryDB API."""
    BASE_URL = "https://poetrydb.org"
    
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

class PoetryBlogGenerator:
    def __init__(self):
        """Initialize using environment variables for configuration."""
        self.openai_api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(api_key=self.openai_api_key)
        self.poetry_db = PoetryDB()
        
        # Define paths
        self.output_dir = Path('_posts')
        self.output_dir.mkdir(exist_ok=True)
        
        self.all_authors = [
            "Edgar Allan Poe", "Elizabeth Barrett Browning", "Emily Bronte",
            "Emily Dickinson", "Christina Rossetti", "Matthew Arnold",
            "Robert Browning", "Alfred, Lord Tennyson", "Percy Bysshe Shelley",
            "William Wordsworth", "Wilfred Owen", "Rupert Brooke",
            "Joyce Kilmer", "Paul Laurence Dunbar", "Edward Thomas"
        ]

        # Basic poetic forms for reference
        self.poetic_forms = [
            "Sonnet", "Haiku", "Villanelle", "Ballad", "Free Verse", 
            "Ghazal", "Tanka", "Cinquain", "Limerick", "Ode",
            "Pantoum", "Rondeau", "Terza Rima", "Triolet"
        ]

    def get_poem_analysis(self, poem: Dict[str, Any]) -> str:
        """Get detailed poem analysis from GPT with specific line references."""
        try:
            prompt = f"""
            Analyze this poem with specific line references and detailed explanations:

            Title: {poem['title']}
            Author: {poem['author']}

            {chr(10).join(poem['lines'])}

            Provide a thorough analysis using exactly these section headings and format:

            # Form, Structure, Meter, and Rhyme
            [Your analysis of form, structure, meter, and rhyme here]

            # Themes and Imagery
            [Your analysis of themes and imagery here]

            # Literary Devices
            [Your analysis of literary devices here]

            # Historical and Personal Context
            [Your analysis of historical and personal context here]

            # Deep Reading
            [Your deeper analysis here]

            Make each section thorough and detailed. Use line references and specific examples.
            Do not use asterisks for emphasis - use proper markdown headers with # symbols.
            Write in an engaging, accessible style while maintaining analytical depth.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Process the response to ensure consistent formatting
            analysis = response.choices[0].message.content
            
            # Replace any remaining asterisks with proper markdown
            analysis = analysis.replace('**', '')
            
            # Ensure section headers are properly formatted
            sections = ['Form, Structure, Meter, and Rhyme', 'Themes and Imagery', 
                    'Literary Devices', 'Historical and Personal Context', 'Deep Reading']
            
            for section in sections:
                analysis = analysis.replace(f'# {section}', f'### {section}')
                
            return analysis

        except Exception as e:
            logger.error(f"Error getting poem analysis: {str(e)}")
            return "Analysis unavailable at this time."

    def get_writing_prompt(self) -> Dict[str, str]:
        """Generate a creative writing prompt using GPT."""
        try:
            form = random.choice(self.poetic_forms)
            
            prompt = f"""
            Create an inspiring poetry writing prompt. Use this poetic form: {form}

            Return the response in this exact JSON format:
            {{
                "form": "{form}",
                "structure": "Brief description of the form's structure",
                "rhyme_scheme": "Description of rhyme scheme if applicable",
                "prompt": "A creative and specific writing prompt"
            }}

            Make the prompt specific, evocative, and imaginative. Focus on sensory details, emotions, or narrative moments.
            The prompt should inspire both beginning and experienced poets.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.9
            )
            
            # Parse the response as JSON
            try:
                prompt_data = json.loads(response.choices[0].message.content)
                required_keys = ["form", "structure", "rhyme_scheme", "prompt"]
                if not all(key in prompt_data for key in required_keys):
                    raise ValueError("Missing required keys in prompt data")
                return prompt_data
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing prompt JSON: {str(e)}")
                # Fallback to basic prompt if JSON parsing fails
                return {
                    "form": form,
                    "structure": "Traditional form",
                    "rhyme_scheme": "Variable",
                    "prompt": "Write about a meaningful personal experience"
                }
                
        except Exception as e:
            logger.error(f"Error getting writing prompt: {str(e)}")
            return {
                "form": "Free Verse",
                "structure": "No fixed structure",
                "rhyme_scheme": "No fixed rhyme scheme",
                "prompt": "Write about something that moved you today"
            }

    def select_daily_poems(self) -> List[Dict[str, Any]]:
        """Select 3 random poems for today."""
        selected_poems = []
        available_authors = random.sample(self.all_authors, 3)

        for author in available_authors:
            poems = self.poetry_db.get_poems_by_author(author)
            if poems:
                selected_poem = random.choice(poems)
                selected_poems.append(selected_poem)

            if len(selected_poems) == 3:
                break

        return selected_poems

    def generate_post(self, poems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a blog post with poems and analyses."""
        current_date = datetime.now()
        analyses = [self.get_poem_analysis(poem) for poem in poems]
        writing_prompt = self.get_writing_prompt()

        post_data = {
            "date": current_date.strftime("%Y-%m-%d"),
            "title": f"Daily Poetry Collection - {current_date.strftime('%B %d, %Y')}",
            "poems": [
                {
                    "title": poem["title"],
                    "author": poem["author"],
                    "lines": poem["lines"],
                    "analysis": analysis
                }
                for poem, analysis in zip(poems, analyses)
            ],
            "writing_prompt": writing_prompt
        }

        return post_data

    def save_post(self, post_data: Dict[str, Any]):
        """Save the post as a markdown file with YAML front matter."""
        date = post_data["date"]
        filename = f"{date}-daily-poetry.md"
        filepath = self.output_dir / filename

        # Create YAML front matter
        front_matter = {
            "layout": "post",
            "title": post_data["title"],
            "date": f"{date} 00:00:00 +0000",
            "categories": ["poetry", "daily"]
        }

        content = ["---"]
        content.extend([f"{k}: {v}" for k, v in front_matter.items()])
        content.append("---")
        content.append("")

        # Add poems and analyses
        for poem in post_data["poems"]:
            content.append(f"## {poem['title']} by {poem['author']}")
            content.append("")
            content.append("```")
            content.extend(poem["lines"])
            content.append("```")
            content.append("")
            content.append("### Analysis")
            content.append("")
            content.append(poem["analysis"])
            content.append("")

        # Add writing prompt
        prompt = post_data["writing_prompt"]
        content.append("## Today's Writing Challenge")
        content.append("")
        content.append(f"**Form:** {prompt['form']}")
        content.append(f"**Structure:** {prompt['structure']}")
        content.append(f"**Rhyme Scheme:** {prompt['rhyme_scheme']}")
        content.append("")
        content.append(f"*Prompt: {prompt['prompt']}*")
        content.append("")

        # Write the file
        filepath.write_text("\n".join(content))
        logger.info(f"Saved blog post to {filepath}")

    def generate_daily_post(self):
        """Generate and save today's poetry blog post."""
        poems = self.select_daily_poems()
        if not poems:
            logger.error("No poems were selected")
            return

        post_data = self.generate_post(poems)
        self.save_post(post_data)

if __name__ == "__main__":
    PoetryBlogGenerator().generate_daily_post()