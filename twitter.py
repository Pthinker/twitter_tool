#!/usr/bin/env python

import json
import re
import datetime
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream, TweepError
from random import randint
import urllib2
import logging

import config
import db


auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)

gco_id = "585858558588558"
station_id = "25TV"
reply_text = "Hi here is your voucher:"
reply_url = "www.gcotelecom.com"

# logging
logging.basicConfig(filename='twitter.log',level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

""" 
Depreciated
"""
def get_mention():
    session = db.get_session()
    print "entrem a getmention"
    pattern = re.compile("(\+\w+)")
    mentions = api.mentions_timeline(count=100)
    for mention in mentions:
        if session.query(db.SenderAccount).get(mention.id) is not None:
            continue

        record = db.SenderAccount(twitter_handle="lovely_local_tv")
        record.id = mention.id
        record.sender_twitter_handle = mention.user.screen_name
        record.created_at = mention.created_at
        record.sender_data = json.dumps(mention.user._json)

        m = pattern.search(mention.text)
        if m and len(m.groups())>0:
            record.code = m.group(0)

        session.add(record)

        following_ids = api.friends_ids(screen_name = mention.user.screen_name)
        for fid in following_ids:
            user = api.get_user(fid)
            if user.screen_name is None:
                continue

            row = db.SenderFollowing(twitter_handle="lovely_local_tv")
            row.sender_twitter_handle = mention.user.screen_name
            row.following = user.screen_name
            session.add(row)

    session.commit()
    session.close()

def get_rate_status():
    return api.rate_limit_status()

	
class Listener(StreamListener):
			

	def on_data(self, data):

	    tweet = json.loads(data.strip())
	    retweeted = tweet.get('retweeted')
	    from_self = tweet.get('user', {}).get('screen_name', '') == config.twitter_account

            if retweeted is not None and not retweeted and not from_self:
                session = db.get_session()
            	pattern = re.compile("(\+\w+\d\d)")
            
            	sender = tweet.get('user', None)
            
            	current_ts = datetime.datetime.now()
            
	        # save tweet sender data
                row = session.query(db.SenderAccount).filter_by(sender_twitter_id=sender["id"]).first()
                print row
		if row is None:
                   record = db.SenderAccount()
                   record.sender_twitter_id = sender["id"]
                   record.sender_twitter_handle = sender["screen_name"]
                   record.gco_internal_id = gco_id
                   record.triggered_from = station_id
                   record.sender_data = json.dumps(tweet["user"])
                   record.created_at = current_ts
                   session.add(record)
            
	        # save operation data
                op_record = db.Operations()
                op_record.account = config.twitter_account
                op_record.is_closed = False
                op_record.user_id = sender["id"]
                op_record.user_gco_internal_id = gco_id
                op_record.source="twitter"

                code = None
                reply_pin = None
                reply_code = None
                error = None
            
		m = pattern.search(tweet["text"])
                if m and len(m.groups())>0:
                   code = m.group(0)
                   if code[0] == "+"  and int(code[6:]) >= 0 and int(code[6:]) <= 99:  
		   	twitCode = code[1:6]
		   	#print twitCode
			#existsCode = session.query(db.Codes).filter(code == twitCode).first()
		        existsCode = session.query(db.Codes).filter_by(code=twitCode).first()
                        #print existsCode
		        if existsCode is not None:
		            #print "dins checkCode"
		            reply_code = code
                        else:
                            code = "ERROR3"
                            error = "ERROR3"
                   else:
			code = "ERROR3"
                        error = "ERROR3"
                elif "+" in tweet["text"]:
                   code = "ERROR2"
                   error = "ERROR2"
                else:
                   code = "ERROR1"
                   error = "ERROR1"
                op_record.code = code
                op_record.reply_code = reply_code
                op_record.pin = reply_pin
                op_record.url = reply_url
                op_record.media = station_id
                op_record.created_at = current_ts
                op_record.timeout_at = current_ts + datetime.timedelta(seconds=180) # time out in 3 mins
                op_record.reply_ack = True
                op_record.click_ack = False

                session.add(op_record)
            
                # save sender twitter following data
                try:
                   following_ids = api.friends_ids(screen_name = sender["screen_name"])
                   row = session.query(db.SenderFollowing).filter_by(sender_twitter_id=sender["id"]).first()
                   
                   if row is not None:
                      row.following = ",".join(map(str, following_ids))
                      row.created_at = current_ts
                   else:
                      row = db.SenderFollowing()
                      row.sender_twitter_id = sender["id"]
                      row.following = ",".join(map(str, following_ids))
                      row.created_at = current_ts
                      session.add(row)
                except TweepError as e: # in case of exceeding rate limit
                   logging.error(e)

                session.commit()
                session.close()
            
                content = ""
                if error is None:
                   tweet_reply_code = reply_code
                   content = "%s code: %s, destination URL %s @%s" % (reply_text, tweet_reply_code, reply_url, sender["screen_name"])
                 
                elif error == "ERROR1":
                   content = "No code found inside your twitt. Check FAQs on WWW.FHFHHF.COM or resend that on TV screen. @%s" % sender["screen_name"]
                elif error == "ERROR2":
                   content = "Wrong code syntax inside your twitt. Check FAQs WWW.FHFHHF.COM or resend that in TV screen checking spelling. @%s" % sender["screen_name"]
                elif error == "ERROR3":
                   content = "The code supplied is not correct. Check FAQs on WWW.FHFHHF.COM or resend strictly that shown on TV screen. @%s" % sender["screen_name"]

                try:
                   api.update_status(content, tweet["id"])
                except TweepError as e:
                   logging.error(e)


def main():
    while True:
        try:
            stream_listener = Listener()
            twitter_stream = Stream(auth, stream_listener)
            twitter_stream.userstream(_with="user")
        except TweepError as e:
            logging.error(e)

if __name__ == "__main__":
    main()

