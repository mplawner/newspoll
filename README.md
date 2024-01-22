# News Poll Poster

## Introduction
This project consists of a Python script (`main.py`) designed to automate the posting of polls and related content to social media platforms, specifically Mastodon and Twitter. The script fetches the latest articles from an RSS feed, generates poll questions and hashtags using OpenAI's GPT, and then posts them to the specified social media accounts.

## Features
- Fetches latest articles from a specified RSS feed.
- Generates poll questions and hashtags using OpenAI's GPT.
- Posts to Mastodon and Twitter (with the ability to selectively disable each).
- Customizable through a configuration file.

## Quick Start Using Docker Compose

Get started quickly with `newspoll` using Docker. Follow these steps to set up and run the application in a Docker container:

### Prerequisites

- Docker installed on your system.

### Setup

1. **Download the `docker-compose.yml` File**:
   - Download the `docker-compose.yml` file from the repository to a directory on your machine.

2. **Download the Sample Environment File**:
   - Download the `sample.env` file from the repository.
   - Rename `sample.env` to `.env`.

3. **Configure the Environment Variables**:
   - Open the `.env` file in a text editor.
   - Fill in the required parameters. This file contains environment variables that the Docker container will use.

4. **Update `docker-compose.yml` (If Needed)**:
   - Open the `docker-compose.yml` file in a text editor.
   - Modify the `docker-compose.yml` file to suit your setup.
   - Aside from Mastodon and/or Twitter credentials, note that in the sample file, Mastodon is enabled but only publishing to direct, and Twitter is disabled. Update those settings as required when you want to go live. (You'll likely want to change MASTODON_POST_VISIBILITY to public, and TWITTER_ENABLED to true.) 

### Running the Application

1. **Start the Application**:
   - Open a terminal and navigate to the directory where your `docker-compose.yml` and `.env` files are located.
   - Run the following command to start the application:

     ```bash
     docker compose up -d
     ```

   - This command will download the Docker image from GitHub Container Registry and start the `newspoll` service in the background.

2. **Verify the Application is Running**:
   - Run `docker compose ps` to ensure the `newspoll` service is up and running.

3. **View Logs (Optional)**:
   - To view the application logs, run:

     ```bash
     docker compose logs -f
     ```

### Profit!

- Your `newspoll` application is now running in a Docker container. Enjoy the simplicity and flexibility of Dockerized deployment!

## Command Line Installation
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
