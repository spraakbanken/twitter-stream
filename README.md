# Twitter Stream

A script for collecting tweets using Twitter's streaming API. The result is saved as JSON.

## Requirements

* Python 3
* [Twarc](https://github.com/DocNow/twarc): `pip3 install twarc`
* A twitter developer account, and one or more apps.
  To create a twitter app, follow the guide at
  <http://docs.inboundnow.com/guide/create-twitter-application>

## Instructions

Copy the file `track-swedish-tweets.txt` into a file `track-XXX.txt`, and modify it 
as you please. The authentication keys can be found in your twitter app info page.

Run `python3 collect_tweets.py track-XXX.txt` to start the collection.
Press `Ctrl-C` to stop the collection and terminate the script.

If you want to collect for a longer time, run `test-and-restart-collection.sh`.
Put the script in your crontab if you want it to restart if it stops:

```
*/1 * * * * /PATH/TO/test-and-restart-collection.sh >/dev/null 2>&1
```

The data is stored as JSON files in monthly folder in the base folder that is 
specified by `track-XXX.txt`. Every tweet is one JSON object on a single line,
and there is one file per hour.


