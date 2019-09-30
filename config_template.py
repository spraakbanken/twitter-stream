# The tweets collected will match the three filters combined like:
# '(word_filter OR location_filter) AND language_filter'

# Words or hashtags to filter by (maximum 400)
word_filter = ["example", "#example"]

# The path of an optional text file (UTF-8) with one keyword per line to append to word_filter
word_file = ""

# Locations to filter by
location_filter = ["11.03", "55.19", "24.92", "69.29"]

# Languages to filter by
# https://developer.twitter.com/en/docs/developer-utilities/supported-languages/api-reference/get-help-languages
language_filter = ["en"]

# Use https://developer.twitter.com/en/apps to get the following information
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

# Path where JSON output will be saved
out_path = "data"

# Prefix to add to file names
file_prefix = "twitter-"

# Maximum number of tweets to save per file
tweets_per_file = 5000

# Whether to print tweets to the terminal as they are collected
print_tweets = False
