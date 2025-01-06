# scripts/generate_poems.py
import os
import json
import random
import requests
from datetime import datetime
from openai import OpenAI

class PoetryGenerator:
    def __init__(self):
        self.authors = [
            "Edgar Allan Poe", "Elizabeth Barrett Browning", "Emily Bronte",
            "Emily Dickinson", "Christina Rossetti", "Matthew Arnold",
            "Robert Browning", "Alfred, Lord Tennyson", "Percy Bysshe Shelley",
            "William Wordsworth", "Wilfred Owen", "Rupert Brooke",
            "Joyce Kilmer", "Paul Laurence Dunbar", "Edward Thomas"
        ]
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.poetic_forms = [
            {
                "name": "Sonnet",
                "structure": "14 lines, typically in iambic pentameter",
                "rhyme_scheme": "Various schemes including Shakespearean (ABAB CDCD EFEF GG) or Petrarchan (ABBAABBA CDECDE)",
                "prompt": "Write about a transformative moment in nature"
            },
            {
                "name": "Haiku",
                "structure": "3 lines with syllables 5-7-5",
                "rhyme_scheme": "No specific rhyme scheme",
                "prompt": "Capture a fleeting seasonal moment"
            },
            {
                "name": "Villanelle",
                "structure": "19 lines with repeating refrains",
                "rhyme_scheme": "ABA ABA ABA ABA ABA ABAA",
                "prompt": "Express an obsessive thought or memory"
            }
        ]

    def get_poems_by_author(self, author):
        try:
            response = requests.get(
                f"https://poetrydb.org/author/{requests.utils.quote(author)}"
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching poems for {author}: {e}")
            return []

    def analyze_poem(self, poem):
        try:
            prompt = f"""
            Analyze this poem:

            Title: {poem['title']}
            Author: {poem['author']}

            {chr(10).join(poem['lines'])}

            Provide a thorough analysis covering:
            1. Form and Structure
            2. Key Themes and Imagery
            3. Literary Devices
            4. Historical and Personal Context
            5. Deep Reading

            Format the response in clear sections with specific examples.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating analysis: {e}")
            return "Analysis unavailable"

    def generate_daily_content(self):
        selected_authors = random.sample(self.authors, 3)
        daily_poems = []

        for author in selected_authors:
            poems = self.get_poems_by_author(author)
            if poems:
                selected_poem = random.choice(poems)
                analysis = self.analyze_poem(selected_poem)
                daily_poems.append({
                    "title": selected_poem["title"],
                    "author": selected_poem["author"],
                    "lines": selected_poem["lines"],
                    "analysis": analysis
                })

        daily_content = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "poems": daily_poems,
            "writing_prompt": random.choice(self.poetic_forms)
        }

        # Ensure the data directory exists
        os.makedirs("data", exist_ok=True)

        # Save the daily content
        with open("data/daily-poems.json", "w") as f:
            json.dump(daily_content, f, indent=2)

        # Save to archive with date
        archive_path = f"data/archive/{daily_content['date']}.json"
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        with open(archive_path, "w") as f:
            json.dump(daily_content, f, indent=2)

if __name__ == "__main__":
    generator = PoetryGenerator()
    generator.generate_daily_content()
