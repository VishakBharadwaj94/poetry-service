# Daily Poetry Blog Generator

An automated poetry blog that publishes daily poems with AI-powered analysis using GitHub Actions and GitHub Pages. Each day, the system selects three random poems from classic authors, generates detailed literary analysis using GPT-3.5, and creates a new blog post with a creative writing prompt.

## Features

- Automated daily posts featuring three carefully selected poems
- Detailed AI-powered analysis of each poem's structure, themes, and literary devices
- Daily writing prompts to inspire creativity
- Responsive Jekyll-based blog design
- Dark mode support
- Fully automated through GitHub Actions
- Free hosting with GitHub Pages

## Setup

### Prerequisites

- GitHub account
- OpenAI API key
- Basic familiarity with Git and GitHub

### Installation

1. Fork this repository or create a new one using it as a template

2. Clone your repository locally:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

3. Configure GitHub Pages:
   - Go to your repository settings
   - Navigate to "Pages" section
   - Select the main/master branch as source
   - Choose root directory as publishing source
   - Save the settings

4. Set up required secrets:
   - Go to repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add new repository secret:
     - Name: `OPENAI_API_KEY`
     - Value: Your OpenAI API key

5. Update `_config.yml`:
   - Replace `your-username` with your GitHub username
   - Replace `your-repo-name` with your repository name

6. Push your changes:
```bash
git add .
git commit -m "Initial setup"
git push origin main
```

### Local Development

1. Install required Python packages:
```bash
pip install requests openai
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY='your-api-key'
```

3. Run the blog generator manually:
```bash
python generate_blog.py
```

4. To test the Jekyll site locally:
```bash
gem install bundler jekyll
bundle install
bundle exec jekyll serve
```

## How It Works

### Daily Workflow

1. GitHub Actions triggers the workflow daily at midnight UTC
2. The script selects three random poems from the configured list of authors
3. For each poem:
   - Fetches the full text from PoetryDB
   - Generates detailed analysis using GPT-3.5
4. Creates a new markdown post in `_posts/` directory
5. Commits and pushes changes to the repository
6. GitHub Pages automatically builds and deploys the updated site

### File Structure

```
your-repo/
├── _posts/                    # Generated blog posts
├── .github/
│   └── workflows/
│       └── daily-poetry.yml   # GitHub Actions workflow
├── _layouts/                  # Jekyll layouts
├── _includes/                 # Jekyll includes
├── assets/
│   └── css/                  # Custom styles
├── generate_blog.py          # Main script
├── _config.yml               # Jekyll configuration
└── README.md                 # This file
```

### Customization

#### Adding New Authors

Edit the `all_authors` list in `generate_blog.py`:

```python
self.all_authors = [
    "Edgar Allan Poe",
    "Emily Dickinson",
    # Add more authors...
]
```

#### Modifying Poetry Forms

Edit the `poetic_forms` list in `generate_blog.py` to add or modify writing prompt templates:

```python
self.poetic_forms = [
    {
        "name": "Sonnet",
        "structure": "14 lines...",
        "rhyme_scheme": "ABAB...",
        "example_prompt": "Write about..."
    },
    # Add more forms...
]
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Poetry data provided by [PoetryDB](https://poetrydb.org/)
- Analysis powered by OpenAI's GPT-3.5
- Built with Jekyll and GitHub Pages
- Inspired by the classic works of renowned poets