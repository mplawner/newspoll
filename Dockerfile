# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get -y install cron

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY main.py /usr/src/app/
COPY update-crontab.sh /usr/src/app/
COPY requirements.txt /usr/src/app/

# Give execution rights on the cron script
RUN chmod +x /usr/src/app/update-crontab.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the update-crontab script when the container launches
CMD ["./update-crontab.sh"]