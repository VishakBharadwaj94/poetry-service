# Daily Poetry Analysis Service

A GitHub Actions-based service that sends you three poems daily via email, complete with AI-powered analysis. This service uses PoetryDB for poems and OpenAI's GPT for in-depth literary analysis.

## Features

- Automatically sends 3 poems daily at a specified time
- Sources poems from PoetryDB's extensive collection
- Uses GPT-3.5-turbo for detailed analysis including:
  - Form and structure
  - Meter and rhyme scheme
  - Key themes and imagery
  - Literary devices
  - Historical context
- Configurable preferred authors list
- Runs automatically via GitHub Actions

## Prerequisites

To use this service, you'll need:
- A GitHub account (free)
- A Gmail account
- A Gmail app-specific password
- An OpenAI account with:
  - A valid credit card on file
  - API access enabled
  - An API key (new accounts receive $5 in free credit)

Note: OpenAI requires a credit card for API access even if you plan to only use the free credit. The card will not be charged until you exceed the free credit limit.

## Costs

The service is very cost-effective:
- GPT-3.5-turbo costs approximately $0.0015 per poem analysis
- 3 poems per day = $0.0045 daily
- Approximately $0.14 per month
- First month likely free with OpenAI's $5 starter credit
- Your credit card will only be charged if you exceed the free credit

## Setup Instructions

### 1. Fork/Clone the Repository
```bash
git clone https://github.com/yourusername/poetry-service.git
cd poetry-service
```

### 2. Set Up OpenAI Account and Get API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Add a valid credit card to your account
4. Enable API access in your account settings
5. Click your profile icon → "View API keys"
6. Click "Create new secret key"
7. Copy the key (save it - you won't be able to see it again)

### 3. Create Gmail App Password
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification → App passwords
3. Create a new app password
4. Save this password for the next step

### 4. Configure GitHub Secrets
Add the following secrets to your repository (Settings → Secrets and variables → Actions):

- `GMAIL_ADDRESS`: Your Gmail address
- `GMAIL_APP_PASSWORD`: The app-specific password you created
- `OPENAI_API_KEY`: Your OpenAI API key

### 5. Customize Settings (Optional)

#### Modify Preferred Authors
Edit the `preferred_authors` list in `poetry_service.py`:
```python
self.preferred_authors = [
    "Emily Dickinson",
    "Robert Frost",
    "William Shakespeare",
    # Add or remove authors as desired
]
```

#### Change Email Schedule
Edit the cron schedule in `.github/workflows/poetry_service.yml`:
```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Runs at 9:00 AM UTC
```

For help with cron syntax, visit [crontab.guru](https://crontab.guru/).

### 6. Deploy
Push your changes to GitHub:
```bash
git add .
git commit -m "Configure poetry service"
git push
```

## Usage

The service will automatically run daily according to your configured schedule. You can also:

1. Run manually through GitHub:
   - Go to your repository
   - Click "Actions"
   - Select "Daily Poetry Service"
   - Click "Run workflow"

2. Monitor runs:
   - Check the Actions tab in your repository
   - View logs for any failures or issues
   - Monitor OpenAI usage in your OpenAI dashboard

## Troubleshooting

### Common Issues

1. **OpenAI API Issues**
   - Verify credit card is valid and not expired
   - Check if you've exceeded free credit limit
   - Ensure API access is enabled in your account
   - Verify API key is valid and properly set in secrets

2. **Emails not sending**
   - Check if Gmail app password is correct
   - Verify email address in secrets
   - Check GitHub Actions logs for errors

3. **No poems being fetched**
   - Ensure preferred authors exist in PoetryDB
   - Check PoetryDB API status
   - Verify internet connectivity in Actions logs

### Getting Help

If you encounter issues:
1. Check the Actions logs for error messages
2. Review the Issues tab in this repository
3. Create a new issue with:
   - Description of the problem
   - Relevant logs (without sensitive information)
   - Steps to reproduce

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PoetryDB](https://poetrydb.org/) for providing the poetry database
- [OpenAI](https://openai.com/) for GPT API
- All the poets whose works are included

## Security Notes

- Never commit sensitive information like API keys or passwords
- Always use GitHub secrets for credentials
- Regularly rotate your Gmail app password
- Monitor GitHub Actions usage if using a private repository
- Keep an eye on OpenAI API usage and set usage limits if needed
- Ensure your OpenAI account has billing notifications enabled
- Review OpenAI's billing dashboard regularly to avoid unexpected charges
