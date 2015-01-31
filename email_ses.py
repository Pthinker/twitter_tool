#!/usr/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import datetime
from random import randint
import sys
import os
import re
import logging
from gmail import Gmail

import config
import db


logging.basicConfig(filename='email.log',level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

from_addr = "davidzhang.seu@gmail.com"
#to_addr = "weizhangnd@gmail.com"
to_addr = "fcachadina@gcotelecom.com"
gco_id = "585858558588558"
station_id = "25TV"
reply_url = "www.gcotelecom.com"

def check_inbox():
    g = Gmail()
    g.login(config.GMAIL_USER, config.GMAIL_PWD)
    
    msg = []
    if g.logged_in:
        emails =  g.inbox().mail(unread=True)
        for email in emails:
            email.fetch()
            subject = email.subject.strip()
            body = email.body.strip()
            fr = email.fr.strip()
            if len(subject) > 0:
                msg.append((fr, subject, body))
            email.read()
        g.logout()
    else:
        logging.error("Failed to login to gmail inbox.")
    
    return msg

def compose_email(from_addr, to_addr):
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = "test email"
    
    if not os.path.exists(config.JSON_FPATH):
        logging.error("%s does not exist, please check!" % config.JSON_FPATH)
        sys.exit(1)

    json_data = None
    try:
        with open(config.JSON_FPATH) as fh:
            json_data = json.load(fh)
    except ValueError:
        logging.error("%s: incorrect json format" % config.JSON_FPATH)
        sys.exit(1)

    content = """\
        <html>
            <body>
                <p>brand logo: <img src="%s"></p>
                <p>Channel: %s</p>
                <p>reply code: +hao123</p>
                <p>reply url: <a href="%s">%s</a></p>
            </body>
        </html>
    """ % (json_data["mediaDistribution"][0]["channelLogoUrl"], json_data["mediaDistribution"][0]["channelName"], reply_url, reply_url)

    body = MIMEText(content, 'html')
    msg.attach(body)
    return msg

def save_operation():
    session = db.get_session()
    current_ts = datetime.datetime.now()

    # save operation data
    op_record = db.Operations()
    op_record.is_closed = False
    global gco_id
    op_record.user_gco_internal_id = gco_id
    op_record.source="email"
    op_record.code = "test_code"
    reply_code = str(randint(10000, 99999))
    reply_pin = str(randint(1000, 9999))
    op_record.pin = reply_pin
    op_record.reply_code = reply_code
    global reply_url
    global station_id
    op_record.url = reply_url
    op_record.media = station_id
    op_record.created_at = current_ts
    op_record.timeout_at = current_ts + datetime.timedelta(seconds=180) # time out in 3 mins
    op_record.reply_ack = True
    op_record.click_ack = False

    session.add(op_record)
    session.commit()
    session.close()

def send_email(emails):
    server = smtplib.SMTP(
        host = config.SES_HOST, 
        port = config.SES_PORT,
        timeout = 10
    )

    global from_addr
 
    server.set_debuglevel(1)
    server.starttls()
    server.ehlo()
    server.login(config.SES_USER, config.SES_PWD)
    
    pattern = re.compile("(\+\w+)")
    for (to_addr, subject, body) in emails:
        # TODO: get code from subject or body
        :   
        if found:
            msg = compose_email(from_addr, to_addr)
            server.sendmail(from_addr, to_addr, msg.as_string())

        save_operation()
    
    server.quit()

def main():
    emails = check_inbox()
    send_email(emails)

if __name__ == "__main__":
    main()
