# newspoll
Script to automatically create a poll from the latest article in an RSS feed, written by OpenAI, and posted to Mastodon and/or Twitter.

# Installation
pip3 install -r requirements.txt
cp config.ini.sample config.ini

# Edit config.ini
openai: Paste your OpenAI API key here
seed: You can leave this blank, or use one you like. (Seed used to create poll is logged in the log.txt file)
Fill in the Mastodon instance_url, client_id, client_secret, access_token 
post_visibility: One of either ‘direct’ - post will be visible only to mentioned users ‘private’ - post will be visible only to followers ‘unlisted’ - post will be public but not appear on the public timeline ‘public’ - post will be public
poll_expiration: Duration of poll in seconds
hashtags: not yet used, but the plan is to eventually add these to the poll
News - feed: this should be the url of the RSS feed. Be sure to test this (with visibility direct) since not all RSS feeds parse properly.
Fill in the Twitter app info
hashtags: aren't yet used on twitter, either
duration_minutes: how long the poll will last on twitter

# Run
python3 ./main.py 

Optional command line parameters:
--no-twitter: Will not publish to Twitter
--no-mastodon: Will not publish to Mastodon
--config {file}: Can provide an alternative config.ini file. Default if unspecified will be config.ini

