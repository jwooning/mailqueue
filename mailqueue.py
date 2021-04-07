#!/usr/bin/env python3
import os
import time
import threading
import configparser
import smtplib
import email
import email.mime.multipart
import email.mime.text


class MailQueue:
  def __init__(self, maildir, config_path):
    self.maildir = maildir
    self.parse_config(config_path)

    self.smtp = smtplib.SMTP_SSL(self.config['SERVER'], port=self.config['PORT'])
    self.smtp.login(self.config['USERNAME'], self.config['PASSWORD'])

    threading.Thread(target=self.worker).start()

  def parse_config(self, path):
    config = configparser.ConfigParser()
    if not config.read(path):
      print(f'Could not read config at: {path}')
    self.config = {k.upper(): v for k, v in config.items('DEFAULT')}

  def send_smtp(self, to_addr, subject, msg):
    msg_root = email.mime.multipart.MIMEMultipart('alternative')
    msg_root['Subject'] = subject
    msg_root['From'] = self.config['SENDER']
    msg_root['To'] = to_addr

    msg_root.attach(email.mime.text.MIMEText(msg, 'html'))
    self.smtp.sendmail(self.config['SENDER'], [to_addr], msg_root.as_string())

  def worker(self):
    while True:
      res = {}
      for f in os.listdir(self.maildir):
        mail_path = os.path.join(sites_dir, f)
        if os.path.isfile(site_path):
          try:
            with open(mail_path, 'r') as fp:
              to = fp.readline()
              subject = fp.readline()
              msg = fp.read()

            self.send_smtp(to, subject, msg)
            os.remove(mail_path)
          except Exception as e:
            print(e)

      time.sleep(60)
