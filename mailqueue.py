#!/usr/bin/env python3
import os
import time
import threading
import argparse
import configparser
import smtplib
import email
import email.mime.multipart
import email.mime.text


class MailQueue:
  def __init__(self, maildir, faildir, config_path):
    self.maildir = maildir
    self.faildir = faildir
    self.ml_retries = {}
    self.parse_config(config_path)
    self.setup_smtp()

    threading.Thread(target=self.worker).start()

  def parse_config(self, path):
    config = configparser.ConfigParser()
    if not config.read(path):
      print(f'Could not read config at: {path}')
    self.config = {k.upper(): v for k, v in config.items('DEFAULT')}

  def setup_smtp(self):
    self.smtp = smtplib.SMTP_SSL(self.config['SERVER'], port=self.config['PORT'])
    self.smtp.login(self.config['USERNAME'], self.config['PASSWORD'])

  def send_smtp(self, to_addr, subject, msg, is_html=False):
    msg_root = email.mime.multipart.MIMEMultipart('alternative')
    msg_root['Subject'] = subject
    msg_root['From'] = self.config['SENDER']
    msg_root['To'] = to_addr

    mimetype = 'html' if is_html else 'plain'
    msg_root.attach(email.mime.text.MIMEText(msg, mimetype))

    try:
      self.smtp.sendmail(self.config['SENDER'], [to_addr], msg_root.as_string())
    except smtplib.SMTPServerDisconnected:
      print('Lost connection to smtp server, retrying')
      self.setup_smtp()
      self.smtp.sendmail(self.config['SENDER'], [to_addr], msg_root.as_string())

  def worker(self):
    while True:
      res = {}
      for ml in os.listdir(self.maildir):
        mail_path = os.path.join(self.maildir, ml)
        if not ml.startswith('.') and os.path.isfile(mail_path) and os.access(mail_path, os.W_OK):
          try:
            with open(mail_path, 'r') as fp:
              to = fp.readline()
              subject = fp.readline()
              msg = fp.read()

            self.send_smtp(to, subject, msg, is_html=msg.startswith('<html'))
            os.remove(mail_path)
            if ml in self.ml_retries:
              del self.ml_retries[ml]
            print(f'{ml} sent')
          except Exception as e:
            if ml not in self.ml_retries:
              self.ml_retries[ml] = 0
            self.ml_retries[ml] += 1
            print(f'{ml}/{self.ml_retries[ml]} failed: {e}')

            if self.ml_retries[ml] >= int(self.config['RETRIES']):
              print(f'{ml} permanently failed')
              os.rename(mail_path, mail_path.replace(self.maildir, self.faildir))
              del self.ml_retries[ml]

      time.sleep(int(self.config['TIMEOUT']))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Run mailqueue.')
  parser.add_argument('--config', metavar='config', type=str, default='config.ini',
                      help='configuration containing settings')
  parser.add_argument('--maildir', metavar='maildir', type=str, default='maildir',
                      help='directory containing the mail queue')
  parser.add_argument('--faildir', metavar='faildir', type=str, default='faildir',
                      help='directory containing the failed emails')
  args = parser.parse_args()

  MailQueue(os.path.join(os.getcwd(), args.maildir), os.path.join(os.getcwd(), args.faildir), args.config)
