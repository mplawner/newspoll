import configparser
from re import I
import random
import feedparser
from mastodon import Mastodon
import openai
import requests
from bs4 import BeautifulSoup
import logging
import sys
from requests_oauthlib import OAuth1Session
import argparse

# Set up command line arguments
parser = argparse.ArgumentParser(description='Post updates to Mastodon and Twitter.')
parser.add_argument('--no-mastodon', action='store_true', help='Skip posting to Mastodon')
parser.add_argument('--no-twitter', action='store_true', help='Skip posting to Twitter')
parser.add_argument('--config', type=str, default='config.ini', help='Path to config file')

args = parser.parse_args()

# Read configuration
config_file = args.config
config = configparser.ConfigParser()
config.read(config_file)

logging.basicConfig(filename='log.txt', filemode='a', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# OpenAI credentials and parameters
logger.info('Parsing OpenAI credentials')
openai.api_key = config['OpenAI']['openai']
model_name = config['OpenAI']['model']
temperature = float(config['OpenAI']['temperature'])
seed = config['OpenAI'].get('seed')
if seed is None or seed == '':
    seed = random.randint(10000, 99999)
else:
    seed = int(seed)
system_message_content = config['OpenAI']['system_message']

logger.debug('openai.api_key set to: ' + str(openai.api_key))
logger.debug('model_name set to: ' + str(model_name))
logger.debug('temperature set to: ' + str(temperature))
logger.debug('seed set to: ' + str(seed))
logger.debug('system_message_content set to: ' + str(system_message_content))

# Fetch the latest article from the RSS feed
logger.info('Parsing RSS feed')
rss_feed_url = config['News']['feed']  # Assuming the RSS feed URL is stored here
feed = feedparser.parse(rss_feed_url)
if 'title' in feed.feed:
    site_title = feed.feed.title
else:
    site_title = "Unknown Site Title"
    logger.warning("RSS feed does not contain a site title.")
if feed.entries:
    latest_article = feed.entries[0]
    # ... [process the latest article]
else:
    logger.error("The RSS feed contains no entries.")
    sys.exit(1)  # Exit the script due to an empty feed
latest_article_title = latest_article.title
latest_article_summary = latest_article.summary
latest_article_summary_html = latest_article.summary
soup = BeautifulSoup(latest_article_summary_html, 'html.parser')
latest_article_summary = soup.get_text(separator=' ')

latest_article_url = latest_article.link  # Extract the URL
logger.debug('rss_feed_url set to: ' + str(rss_feed_url))
logger.debug('Latest Article Title: ' + str(latest_article_title))
logger.debug('Latest Article Summary: ' + str(latest_article_summary))
logger.debug('Latest Article URL: ' + str(latest_article_url))

# Fetch the full article content
logger.info('Fetching full article content')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get(latest_article_url, headers=headers)
article_content = ''
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    # Modify this line according to the structure of the webpage
    article_body = soup.find('article') or soup.find('div', class_='post-content')
    if article_body:
        article_content = article_body.get_text(strip=True, separator=' ')
        logger.debug('Article content fetched')
    else:
        logger.error('Failed to parse the article content')
        sys.exit(1)  # Exit the program with a status code indicating an error
else:
    logger.error('Failed to fetch article: HTTP ' + str(response.status_code))
    sys.exit(1)  # Exit the program with a status code indicating an error

user_message_content = "Generate a compelling and slightly edgy poll question based on the following news article, followed by three VERY succinct poll options (less than 5 words each). Format the response as: Poll Question: [Your question here] Option 1: [First option] Option 2: [Second option] Option 3: [Third option]."

user_message = {
    "role": "user",
    "content": f"{user_message_content} Article: {article_content}"
}

# Call OpenAI API to generate the poll question and post text
response = openai.ChatCompletion.create(
    model=model_name,
    temperature=temperature,
    seed=seed,
    messages=[{"role": "system", "content": system_message_content}, user_message]
)

response_content = response.choices[0].message['content']
logger.debug('Response: ' + str(response_content))

# Prepare a new user message for generating hashtags
hashtag_message_content = "Generate four generic, high-level, likely commonly used hashtags based on the following news article. At least one should be the name of the countries involved, and at least one should be the name of the people or organizations involved. Format the response as: #hashtag1 #hashtag2 #hashtag3 #hashtag3."

hashtag_user_message = {
    "role": "user",
    "content": f"{hashtag_message_content} Article: {article_content}"
}

# Call OpenAI API to generate hashtags
hashtag_response = openai.ChatCompletion.create(
    model=model_name,
    temperature=temperature,
    seed=seed,
    messages=[{"role": "system", "content": system_message_content}, hashtag_user_message]
)

hashtag_response_content = hashtag_response.choices[0].message['content']
logger.debug('Hashtag Response: ' + str(hashtag_response_content))

# Split the response based on the specified format
parts = response_content.split("Option ")
original_poll_question = parts[0].replace("Poll Question: ", "").strip()
poll_options = [option.partition(": ")[2].strip() for option in parts[1:] if option]
poll_options = [option if len(option) <= 100 else option[:100] for option in poll_options]
logger.debug('Poll question: ' + original_poll_question)
logger.debug('Poll options: ' + str(poll_options))

if not args.no_mastodon:
    # Mastodon credentials
    logger.info('Parsing Mastodon credentials')
    instance_url = config['Mastodon']['instance_url']
    client_id = config['Mastodon']['client_id']
    client_secret = config['Mastodon']['client_secret']
    access_token = config['Mastodon']['access_token']
    post_visibility = config['Mastodon']['post_visibility']
    poll_expiration = config['Mastodon']['poll_expiration']
    mastodon_hashtags = config['Mastodon']['hashtags']

    logger.debug('instance_url set to: ' + str(instance_url))
    logger.debug('client_id set to: ' + str(client_id))
    logger.debug('client_secret set to: ' + str(client_secret))
    logger.debug('access_token set to: ' + str(access_token))
    logger.debug('post_visibility set to: ' + str(post_visibility))

    # Initialize Mastodon API
    logger.info('Initializing Mastodon API')
    mastodon = Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        api_base_url=instance_url
    )

    poll_question = (
        f"In their latest article, {latest_article_title}, {site_title} writes:\n\n"
        f"{latest_article_summary}\n"
        f"Read more: {latest_article_url}\n\n"
        f"{original_poll_question}\n\n"
        f"Feel free to reply and expand on your thoughts.\n"
        f"{hashtag_response_content}\n"
    )
    logger.debug('Mastodon Poll question: ' + poll_question)

    poll = mastodon.make_poll(poll_options, poll_expiration)
    mastodon.status_post(status=poll_question, poll=poll, visibility=post_visibility)
    logger.info('Poll posted to Mastodon')
else:
    logger.info('Skipping Mastodon post')

if not args.no_twitter:
    # Twitter credentials
    logger.info('Parsing Twitter credentials')
    twitter_consumer_key = config['Twitter']['consumer_apikey']
    twitter_consumer_secret = config['Twitter']['consumer_apikeysecret']
    twitter_access_token = config['Twitter']['access_token']
    twitter_access_token_secret = config['Twitter']['access_token_secret']
    twitter_duration_minutes = int(config['Twitter']['duration_minutes'])
    twitter_hashtags = config['Twitter']['hashtags']

    logger.info('Posting poll to Twitter')
    twitter_oauth = OAuth1Session(
        twitter_consumer_key,
        client_secret=twitter_consumer_secret,
        resource_owner_key=twitter_access_token,
        resource_owner_secret=twitter_access_token_secret
    )

    twitter_text = f"{latest_article_title}\n{latest_article_url}\n{hashtag_response_content}\n{original_poll_question}"

    twitter_payload = {
        "text": twitter_text,
        "poll": {
            "options": poll_options,
            "duration_minutes": twitter_duration_minutes
        }
    }

    twitter_response = twitter_oauth.post(
        "https://api.twitter.com/2/tweets",
        json=twitter_payload,
    )

    if twitter_response.status_code != 201:
        logger.error(f"Failed to post poll to Twitter: {twitter_response.status_code} {twitter_response.text}")
    else:
        logger.info("Successfully posted poll to Twitter")
else:
    logger.info('Skipping Twitter post')