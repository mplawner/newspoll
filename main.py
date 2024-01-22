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
import os

# Set Up Logging
loglevel = os.getenv('LOGLEVEL', 'DEBUG').upper()
loglevel_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
logging.basicConfig(level=loglevel, 
                    format='%(asctime)s %(levelname)s: %(message)s', 
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)
logger.info('*** Starting Run ***')
logger.debug('LOGLEVEL: ' + str(loglevel))

# Read Environment Variables
logger.info('Parsing Environment Variables:')

openai_key = os.getenv('OPENAI_API_KEY')
logger.debug('OPENAI_API_KEY: ' + str(openai_key))

model_name = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo-1106')
logger.debug('OPENAI_MODEL: ' + str(model_name))

temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
logger.debug('OPENAI_TEMPERATURE: ' + str(temperature))

seed = int(os.getenv('OPENAI_SEED', random.randint(100000, 999999)))
logger.debug('OPENAI_SEED: ' + str(seed))

system_message_content = os.getenv('OPENAI_SYSTEM_MESSAGE', 'Generate a compelling and slightly edgy poll question and post text based on the latest news article. The poll should be designed to spark discussion and encourage engagement on social media.')
logger.debug('OPENAI_SYSTEM_MESSAGE: ' + str(system_message_content))

rss_feed_url = os.getenv('RSS_FEED_URL')
logger.debug('RSS_FEED_URL: ' + str(rss_feed_url))

cron_frequency = os.getenv('CRON_FREQUENCY')
logger.debug('CRON_FREQUENCY: ' + str(cron_frequency))

mastodon_enabled = os.getenv('MASTODON_ENABLED', 'False').lower() == 'true'
logger.debug('MASTODON_ENABLED: ' + str(mastodon_enabled))

mastodon_instance_url = os.getenv('MASTODON_INSTANCE_URL')
logger.debug('MASTODON_INSTANCE_URL: ' + str(mastodon_instance_url))

mastodon_client_id = os.getenv('MASTODON_CLIENT_ID')
logger.debug('MASTODON_CLIENT_ID: ' + str(mastodon_client_id))

mastodon_client_secret = os.getenv('MASTODON_CLIENT_SECRET')
logger.debug('MASTODON_CLIENT_SECRET: ' + str(mastodon_client_secret))

mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
logger.debug('MASTODON_ACCESS_TOKEN: ' + str(mastodon_access_token))

mastodon_post_visibility = os.getenv('MASTODON_POST_VISIBILITY', 'public')
logger.debug('MASTODON_POST_VISIBILITY: ' + str(mastodon_post_visibility))

mastodon_poll_expiration = int(os.getenv('MASTODON_POLL_EXPIRATION', '86400'))
logger.debug('MASTODON_POLL_EXPIRATION: ' + str(mastodon_poll_expiration))

twitter_enabled = os.getenv('TWITTER_ENABLED', 'False').lower() == 'true'
logger.debug('TWITTER_ENABLED: ' + str(twitter_enabled))

twitter_consumer_key = os.getenv('TWITTER_CONSUMER_APIKEY')
logger.debug('TWITTER_CONSUMER_APIKEY: ' + str(twitter_consumer_key))

twitter_consumer_secret = os.getenv('TWITTER_CONSUMER_APIKEYSECRET')
logger.debug('TWITTER_CONSUMER_APIKEYSECRET: ' + str(twitter_consumer_secret))

twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
logger.debug('TWITTER_ACCESS_TOKEN: ' + str(twitter_access_token))

twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
logger.debug('TWITTER_ACCESS_TOKEN_SECRET: ' + str(twitter_access_token_secret))

twitter_duration_minutes = int(os.getenv('TWITTER_DURATION_MINUTES', '1440'))
logger.debug('TWITTER_DURATION_MINUTES: ' + str(twitter_duration_minutes))

# Fetch the latest article from the RSS feed
logger.info('Parsing RSS feed')
feed = feedparser.parse(rss_feed_url)
if 'title' in feed.feed:
    site_title = feed.feed.title
else:
    site_title = "Unknown Site Title"
    logger.warning("RSS feed does not contain a site title.")
if feed.entries:
    latest_article = feed.entries[0]
else:
    logger.error("The RSS feed contains no entries. Aborting.")
    sys.exit(1) 
latest_article_title = latest_article.title
logger.debug('Latest Article Title: ' + str(latest_article_title))
#latest_article_summary = latest_article.summary # I believe this is unnecessary
latest_article_summary_html = latest_article.summary
logger.debug('Cleaning up the article summary')
soup = BeautifulSoup(latest_article_summary_html, 'html.parser')
latest_article_summary = soup.get_text(separator=' ')
logger.debug('Latest Article Summary: ' + str(latest_article_summary))
latest_article_url = latest_article.link  
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
    article_body = soup.find('article') or soup.find('div', class_='post-content')
    if article_body:
        article_content = article_body.get_text(strip=True, separator=' ')
        logger.debug('Article content fetched')
    else:
        logger.error('Failed to parse the article content. Aborting.')
        sys.exit(1) 
else:
    logger.error('Failed to fetch article. Abording. Error Code: HTTP ' + str(response.status_code))
    sys.exit(1)

# Generate the Poll Question, Options, and Hashtags
openai.api_key = openai_key

logger.info('Generating Poll Question, Options')
user_message_content = "Generate a compelling and slightly edgy poll question based on the following news article, followed by three VERY succinct poll options (less than 5 words each). Format the response as: Poll Question: [Your question here] Option 1: [First option] Option 2: [Second option] Option 3: [Third option]."
user_message = {
    "role": "user",
    "content": f"{user_message_content} Article: {article_content}"
}
response = openai.ChatCompletion.create(
    model=model_name,
    temperature=temperature,
    seed=seed,
    messages=[{"role": "system", "content": system_message_content}, user_message]
)
response_content = response.choices[0].message['content']
logger.debug('Response: ' + str(response_content))
# Split the response based on the specified format
parts = response_content.split("Option ")
poll_question = parts[0].replace("Poll Question: ", "").strip()
poll_options = [option.partition(": ")[2].strip() for option in parts[1:] if option]
poll_options = [option if len(option) <= 100 else option[:100] for option in poll_options]
logger.debug('Poll question: ' + poll_question)
logger.debug('Poll options: ' + str(poll_options))

logger.info('Generating Hashtags')
hashtag_message_content = "Generate four generic, high-level, likely commonly used hashtags based on the following news article. At least one should be the name of the countries involved, and at least one should be the name of the people or organizations involved. Format the response as: #hashtag1 #hashtag2 #hashtag3 #hashtag3."
hashtag_user_message = {
    "role": "user",
    "content": f"{hashtag_message_content} Article: {article_content}"
}
hashtag_response = openai.ChatCompletion.create(
    model=model_name,
    temperature=temperature,
    seed=seed,
    messages=[{"role": "system", "content": system_message_content}, hashtag_user_message]
)
hashtag_response_content = hashtag_response.choices[0].message['content']
logger.debug('Hashtag Response: ' + str(hashtag_response_content))

if mastodon_enabled:
    # Initialize Mastodon API
    logger.info('Posting to Mastodon')
    mastodon = Mastodon(
        client_id=mastodon_client_id,
        client_secret=mastodon_client_secret,
        access_token=mastodon_access_token,
        api_base_url=mastodon_instance_url
    )

    mastodon_poll_question = (
        f"In their latest article, {latest_article_title}, {site_title} writes:\n\n"
        f"{latest_article_summary}\n"
        f"Read more: {latest_article_url}\n\n"
        f"{poll_question}\n\n"
        f"Feel free to reply and expand on your thoughts.\n"
        f"{hashtag_response_content}\n"
    )
    logger.debug('Mastodon Poll question: ' + mastodon_poll_question)

    mastodon_poll = mastodon.make_poll(poll_options, mastodon_poll_expiration)
    mastodon.status_post(status=mastodon_poll_question, poll=mastodon_poll, visibility=mastodon_post_visibility)
    logger.info('Poll posted to Mastodon')
else:
    logger.info('Skipping Mastodon post')

if twitter_enabled:
    # Twitter credentials
    logger.info('Posting to Twitter')
    twitter_oauth = OAuth1Session(
        twitter_consumer_key,
        client_secret=twitter_consumer_secret,
        resource_owner_key=twitter_access_token,
        resource_owner_secret=twitter_access_token_secret
    )

    twitter_text = f"{latest_article_title}\n{latest_article_url}\n{hashtag_response_content}\n{poll_question}"
    logger.debug('Twitter Poll question: ' + twitter_text)

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
        logger.info("Poll posted to Twitter")
else:
    logger.info('Skipping Twitter post')

logger.info('*** Completed Run ****')