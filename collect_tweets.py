
from twarc import Twarc
import json
import time
import os
import os.path
import sys
import logging
import logging.handlers

start_time = time.time()

assert len(sys.argv) == 2, "Usage: python3 %s CONFIG-FILE.txt" % sys.argv[0]
config_file = sys.argv[1]
base_dir = os.path.dirname(config_file)

track = []
locations = []
languages = []
follow = []
print_tweets = False
twitter_app = data_dir = consumer_key = consumer_secret = access_token = access_token_secret = None
with open(config_file) as F:
    for line in F:
        tokens = line.split()
        if not tokens:
            continue
        cmd = tokens.pop(0) if tokens[0].startswith(":") else None
        if not cmd:
            track.append(" ".join(tokens))
        elif cmd == ":app":
            assert len(tokens) == 1 and not twitter_app
            twitter_app = tokens[0]
        elif cmd == ":dir":
            assert len(tokens) == 1 and not data_dir
            data_dir = tokens[0]
            if not data_dir.endswith("/"): data_dir += "/"
        elif cmd == ":consumer-key":
            assert len(tokens) == 1 and not consumer_key
            consumer_key = tokens[0]
        elif cmd == ":consumer-secret":
            assert len(tokens) == 1 and not consumer_secret
            consumer_secret = tokens[0]
        elif cmd == ":access-token":
            assert len(tokens) == 1 and not access_token
            access_token = tokens[0]
        elif cmd == ":access-token-secret":
            assert len(tokens) == 1 and not access_token_secret
            access_token_secret = tokens[0]
        elif cmd == ":locations":
            assert len(tokens) % 4 == 0
            locations += tokens
        elif cmd == ":languages":
            languages += tokens
        elif cmd == ":follow":
            follow += tokens
        elif cmd == ":print-tweets":
            assert len(tokens) == 0
            print_tweets = True
        elif cmd == "::":
            # this is a comment line
            pass
        else:
            sys.exit("Unknown config line: %r" % line)

assert twitter_app and data_dir and consumer_key and consumer_secret and access_token and access_token_secret

if base_dir:
    data_dir = base_dir + "/" + data_dir
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
log_file = "{}collect-tweets-{:04}-{:02}-{:02}.log".format(data_dir, *time.gmtime(start_time))

## set up the logger, inspired by https://docs.python.org/3/howto/logging-cookbook.html
# get the 'twarc' logger (already used by the twarc module)
log = logging.getLogger('twarc')
log.setLevel(logging.INFO)
# filter out all "keep-alive" logs from twarc
log.addFilter(lambda rec: "keep-alive" not in rec.msg)
# create a file handler that rotates when the log file becomes too large (>1MB)
fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=1000000, backupCount=10, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(fh)


log.info("Twitter app: %s", twitter_app)
log.info("Config file: %s", config_file)
log.info("Logger file: %s", log_file)


dir_template = data_dir + "{time.tm_year:04}-{time.tm_mon:02}/"
file_template = "tweets.{time.tm_year:04}-{time.tm_mon:02}-{time.tm_mday:02}.h{time.tm_hour:02}.json"

log.info("Output dir  template: %s", dir_template)
log.info("Output file template: %s", file_template)
log.info("- " * 50)

# OBSOLETE: this is moved to :follow instead
# OBSOLETE: follow = [t.lstrip("@") for t in track if t.startswith("@")]

if len(track) > 400:
    log.warning("%d tracking terms found, pruning to 400", len(track))
    track = track[:400]


# these checks are really unnecessary because they are already true
assert consumer_key and consumer_secret and access_token and access_token_secret
assert file_template and dir_template
if not dir_template.endswith("/"): dir_template += "/"
assert isinstance(track,     (list, tuple))
assert isinstance(follow,    (list, tuple))
assert isinstance(locations, (list, tuple))
assert isinstance(languages, (list, tuple))

assert len(track) <= 400
assert len(follow) <= 5000
assert len(locations) <= 25*4


## Starting the Twitter server

twarc = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)

log.info("Looking up ids of %d users", len(follow))
follow = [usr["id_str"] for usr in twarc.user_lookup(follow, "screen_name")]

track = ",".join(track)
follow = ",".join(follow)
locations = ",".join(locations)
languages = ",".join(languages)

log.info("Track: %s", track)
log.info("Follow: %s", follow)
log.info("Locations: %s", locations)
log.info("Languages: %s", languages)
log.info("- " * 50)

log.info("Running... Press Ctrl-C to stop.")

tweet_count = 0
F = None
while True:
    try:
        for tweet in twarc.filter(track=track, follow=follow, locations=locations, lang=languages):
            try:
                tweet_time = time.strptime(tweet["created_at"], "%a %b %d %H:%M:%S %z %Y")
            except:
                log.warning("Malformed 'created_at' (%s), using current time instead", tweet.get("created_at"))
                tweet_time = time.gmtime()
            out_dir = dir_template.format(time=tweet_time)
            out_file = out_dir + file_template.format(time=tweet_time)
            if not (F and out_file == F.name):
                if F: F.close()
                if not os.path.exists(out_dir):
                    log.info("Destination dir does not exist and will be created: %s", out_dir)
                    os.makedirs(out_dir)
                log.info("Opening json file: %s", out_file)
                F = open(out_file, "a")
            json.dump(tweet, F)
            F.write("\n")
            tweet_count += 1
            if print_tweets:
                tweet_text = tweet.get("extended_tweet", {}).get("full_text", tweet.get("text", ""))
                log.info("Tweet: %s", tweet_text.replace("\n", " ")[:120])
            # Print progress every 1000 tweets
            if tweet_count % 1000 == 0:
                log.info("%d tweets collected", tweet_count)
    except Exception as e:
        if F: F.close(); F = None
        log.error("Caught exception: %s", e)
        log.error("An error occurred. Retrying in 10 seconds...")
        time.sleep(10)
    except KeyboardInterrupt:
        # Save and exit on Ctrl-C
        if F: F.close()
        total_time = time.time() - start_time
        log.info("Stopped.")
        log.info("- " * 50)
        log.info("Total hours: %.1f", total_time/3600)
        log.info("Total tweets: %d", tweet_count)
        log.info("Tweets per hour: %.1f", (tweet_count / (total_time / (60.0 * 60))))
        sys.exit()
