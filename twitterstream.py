"""
Fetches Twitter data using the live stream API, and saves it as raw JSON data.

Configure by editing config.py.
"""
from twarc import Twarc
import json
import time
import os
import sys
import glob
import re
import config


def log(msg):
    """Print log messages to the screen with current time stamp."""
    print("%s - %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))


def save(data, file_number=0):
    """Save collected data to json file."""
    filename = os.path.join(config.out_path, "%s%06d.json" % (config.file_prefix, file_number))
    log("Saving %s..." % filename)

    with open(filename, mode="a", encoding="UTF-8") as out:
        json.dump(data, out)


if not os.path.exists(config.out_path):
    log("Destination path (%s) does not exist and will be created." % config.out_path)
    os.makedirs(config.out_path)

# Read keywords from word file if available
if config.word_file and os.path.isfile(config.word_file):
    with open(config.word_file, "r", encoding="UTF-8") as wf:
        config.word_filter += [w.strip() for w in wf]
        if len(config.word_filter) > 400:
            log("%d keywords supplied, but only the first 400 will be used." % len(config.word_filter))
            config.word_filter = config.word_filter[:400]

file_count = 0

# Continue counting from last saved file
existing_files = glob.glob(os.path.join(config.out_path, "%s*.json" % config.file_prefix))

if existing_files:
    last_file = sorted(existing_files)[-1]
    last_file_number = re.search(r'%s(\d+)\.json' % config.file_prefix, last_file)
    if last_file_number:
        file_count = int(last_file_number.groups()[0]) + 1

tweet_count = 0
queue = []
twarc = Twarc(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret)
start_time = time.time()
log("Running... Press Ctrl-C to stop.")

while True:
    try:
        for tweet in twarc.filter(track=",".join(config.word_filter),
                                  locations=",".join(config.location_filter),
                                  lang=config.language_filter):
            queue.append(tweet)
            tweet_count += 1
            if config.print_tweets:
                log("Tweet: " + tweet.get("extended_tweet", {}).get("full_text", tweet.get("text", "")))

            # Print progress every 1000 tweets
            if tweet_count % 1000 == 0:
                log("%d tweets collected" % tweet_count)

            if len(queue) >= config.tweets_per_file:
                save(queue, file_number=file_count)
                file_count += 1
                queue = []
    except Exception as e:
        print(e)
        log("An error occurred. Retrying in 10 seconds...")
        time.sleep(10)
    except KeyboardInterrupt:
        # Save and exit on Ctrl-C
        save(queue, file_number=file_count)
        total_time = time.time() - start_time
        log("Stopped.")
        log("Total time: %d sec" % total_time)
        log("Total tweets: %d" % tweet_count)
        log("%.1f tweets per hour" % (tweet_count / (total_time / (60.0 * 60))))
        sys.exit()
