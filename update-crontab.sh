#!/bin/sh

# Export the environment variables to a file that cron will understand
printenv | grep -v "no_proxy" > /etc/environment

# Update the crontab
echo "$CRON_FREQUENCY /usr/local/binpython /usr/src/app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron
chmod 0644 /etc/cron.d/my-cron
crontab /etc/cron.d/my-cron

# Start cron
cron

# Tail the cron.log file in the foreground, to keep the docker running
touch /var/log/cron.log
tail -f /var/log/cron.log
