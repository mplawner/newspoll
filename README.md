# News Poll Poster

## Introduction
This project consists of a Python script (`main.py`) designed to automate the posting of polls and related content to social media platforms, specifically Mastodon and Twitter. The script fetches the latest articles from an RSS feed, generates poll questions and hashtags using OpenAI's GPT, and then posts them to the specified social media accounts.

## Features
- Fetches latest articles from a specified RSS feed.
- Generates poll questions and hashtags using OpenAI's GPT.
- Posts to Mastodon and Twitter (with the ability to selectively disable each).
- Customizable through a configuration file.

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/mplawner/newspoll.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. Rename `config.ini.sample` to `config.ini`.
2. Update `config.ini` with your credentials and preferences for Mastodon, Twitter, and OpenAI.

## Configuration File (`config.ini`)
The `config.ini` file is used to configure various aspects of the script. Rename `config.ini.sample` to `config.ini` and update the following sections and parameters:

### [Mastodon]
This section contains the credentials and settings for posting to Mastodon.
- `instance_url`: The URL of your Mastodon instance.
- `client_id`: Your Mastodon client ID.
- `client_secret`: Your Mastodon client secret.
- `access_token`: Your Mastodon access token.
- `post_visibility`: Visibility of the posts (`public`, `unlisted`, `private`, `direct`). 
- `poll_expiration`: Duration (in seconds) for which the poll will be open. Default is typically 86400 seconds (24 hours).

### [Twitter]
This section contains the credentials for posting to Twitter.
- `consumer_apikey`: Your Twitter consumer API key.
- `consumer_apikeysecret`: Your Twitter consumer API secret.
- `access_token`: Your Twitter access token.
- `access_token_secret`: Your Twitter access token secret.

### [OpenAI]
This section contains the settings for using OpenAI's API.
- `openai`: Your OpenAI API key. 
- `model`: The model used for generating content. Recommendation: gpt-3.5-turbo-1106
- `temperature`: Controls randomness in the AI's responses (between 0 and 1). Recommendation: 0.7.
- `seed`: A seed for deterministic AI responses. If not set, a random value is used.

### [News]
This section configures the RSS feed.
- `feed`: URL of the RSS feed from which the latest news article will be fetched.

Remember to fill in each of these parameters with your own credentials and preferences before running the script.

## Usage
Run the script using:
```bash
python newspoll.py [--no-mastodon] [--no-twitter] [--config CONFIG_FILE]
```
- `--no-mastodon`: Skips posting to Mastodon.
- `--no-twitter`: Skips posting to Twitter.
- `--config CONFIG_FILE`: Specify a different configuration file (default is `config.ini`).

## License
This project is released under the MIT License. See the `LICENSE` file for more details.
```
