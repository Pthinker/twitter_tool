#!/usr/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import codecs
import datetime
from random import randint
import sys
import os
import re
import logging
from gmail import Gmail
import time

import config
import db

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='email.log',level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

from_addr = "davidzhang.seu@gmail.com"
gco_id = "585858558588558"
station_id = "25TV"
reply_url = "www.gcotelecom.com"

def check_inbox():
    g = Gmail()
    g.login(config.GMAIL_USER, config.GMAIL_PWD)
    
    pattern = re.compile("<(.+)>")
    msg = []
    if g.logged_in:
        emails =  g.inbox().mail(unread=True)
        for email in emails:
            email.fetch()
            subject = email.subject.strip()
            body = email.body.strip()
            fr = email.fr.strip()
            m = pattern.search(fr)
            msg.append((m.group(1), subject, body))
            email.read()
        g.logout()
    else:
        logging.error("Failed to login to gmail inbox.")
    
    return msg

def compose_email(from_addr, to_addr, error, reply_code, reply_url):
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = "reply email from lovely_local_tv"
    
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

    if error is None:
        reply_content = "Hi, here is your voucher. code: %s, destination URL %s " % (reply_code, reply_url)
    elif error == "ERROR1":
        reply_content = "No code found inside your email. Check FAQs on WWW.FHFHHF.COM or resend that on TV screen."
    elif error == "ERROR2":
        reply_content = "Wrong code syntax inside your email. Check FAQs WWW.FHFHHF.COM or resend that in TV screen checking spelling"
    elif error == "ERROR3":
        reply_content = "The code supplied is not correct. Check FAQs on WWW.FHFHHF.COM or resend strictly that shown on TV screen."

    ins = json_data["helpers"]["instructions"]["es"]
    content = """\
        <html>
            <body>
                <p>%s</p>
                <p>Channel: %s</p>
                <p>brand logo: <img src="%s"></p>
                <br />
                <p><a href="%s">FAQ</a></p>
                <p><a href="%s">Legal</a></p>
                <p>Disclaimers: %s</p>
                <p>Instructions: %s</p>
            </body>
        </html>
    """ % (reply_content, json_data["mediaDistribution"][0]["channelName"], json_data["mediaDistribution"][0]["channelLogoUrl"], json_data["helpers"]["FAQUrl"]["es"], json_data["helpers"]["LegalUrl"]["es"], json_data["helpers"]["disclaimers"]["es"], ins)
    content = content.encode("UTF-8")
    body = MIMEText(content, 'html')
    msg.attach(body)
    return msg

def send_email(inbox):
    server = smtplib.SMTP(
        host = config.SES_HOST, 
        port = config.SES_PORT,
        timeout = 10
    )

    global from_addr
 
    server.set_debuglevel(0)
    server.starttls()
    server.ehlo()
    server.login(config.SES_USER, config.SES_PWD)
    
    session = db.get_session()
    pattern = re.compile("(\+\w+\d\d)")
    current_ts = datetime.datetime.now()
    
    for (to_addr, subject, body) in inbox:
        found = False
        content = subject + " " + body
        m = pattern.search(content)
        
        code = None
        reply_pin = None
        reply_code = None
        error = None

        if m and len(m.groups())>0:
            code = m.group(0)
            if code[0] == "+" and int(code[6:]) >= 0 and int(code[6:]) <= 99:
                check_code = code[1:6]
                exist_code = session.query(db.Codes).filter_by(code=check_code).first()
                if exist_code is not None:
                    reply_code = code
                else:
                    code = "ERROR3"
                    error = "ERROR3"
        elif "+" in content:
            code = "ERROR2"
            error = "ERROR2"
        else:
            code = "ERROR1"
            error = "ERROR1"

        global reply_url
        msg = compose_email(from_addr, to_addr, error, reply_code, reply_url)
        server.sendmail(from_addr, to_addr, msg.as_string())

        # save operation data
        op_record = db.Operations()
        op_record.is_closed = False
        op_record.account = to_addr
        global gco_id
        op_record.user_gco_internal_id = gco_id
        op_record.source = "email"
        op_record.code = "test_code"
        reply_pin = str(randint(1000, 9999))
        op_record.pin = reply_pin
        op_record.reply_code = reply_code
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
    
    server.quit()

def main():
    while True:
        time.sleep(5)
        inbox = check_inbox()
        send_email(inbox)
        
if __name__ == "__main__":
    main()
