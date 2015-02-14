#!/usr/bin/env python

import time
import tweepy

import config
import db

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)

def main():
    session = db.get_session()
    
    tids = []
    records = session.query(db.SenderFollowing).all()
    for record in records:
        if record.following is not None and len(record.following.strip())>0:
            arr = record.following.split(",")
            tids.extend(arr)
    
    for tid in tids:
        row = session.query(db.TwitterIdToHandle).filter_by(twitter_id=tid).first()
        if row is None:
            user = api.get_user(tid)
            record = db.TwitterIdToHandle()
            record.twitter_id = tid
            record.twitter_handle = user.screen_name
            session.add(record)
            session.commit()

    session.close()

if __name__ == "__main__":
    while True:
        try:
            main()
        except tweepy.TweepError as e:
            print e
        
        time.sleep(900)

