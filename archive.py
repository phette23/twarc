#!/usr/bin/env python

import sys
import json
import config
import oauth2
import logging

logging.basicConfig(filename="archive.log", level=logging.INFO)

consumer = oauth2.Consumer(key=config.consumer_key, secret=config.consumer_secret)
token = oauth2.Token(config.access_token, config.access_token_secret)
client = oauth2.Client(consumer, token)

def sleep_till(t):
    now = time.time()
    if now > t:
        return 
    secs = t - now + 5 # padded with 5 seconds to be safe
    logging.info("sleeping %s seconds for rate limiting" % secs)
    time.sleep(secs)

def search(q, url=None, rate_limit_remaining=None, rate_limit_reset=None):
    if rate_limit_remaining != None and rate_limit_remaining == 0:
        sleep_till(rate_limit_reset)

    # fetch some results
    if not url:
        url = "https://api.twitter.com/1.1/search/tweets.json?q=%s" % q
    resp, content = client.request(url)

    # set rate limit info if not known
    if rate_limit_remaining == None:
        rate_limit_remaining = resp["x-rate-limit-remaining"]
        rate_limit_reset = resp["x-rate-limit-reset"]
    else:
        rate_limit_remaining -= 1

    # return an generator for each result
    results = json.loads(content)
    for status in results["statuses"]:
        yield status
   
    # look for the next set of results
    next_url = results["search_metadata"].get("next_results", None)
    if next_url:
        logging.info("fetching next page of results %s", next_url)
        next_url = "https://api.twitter.com/1.1/search/tweets.json" + next_url
        for status in search(q, next_url, rate_limit_remaining, rate_limit_reset):
            yield status

def archive(statuses, filename):
    fh = open("archive.json", "w")
    for status in search_results:
        url = "http://twitter.com/%s/status/%s"status["user"]["screen_name"], status["id_str"]
        logging.info("archived %s", url)
        fh.write(dumps(status))

if __name__ == "__main__":
    q = sys.argv[1]
    filename = "%s.json" % q
    archive(search(q), filename)