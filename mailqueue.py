#!/usr/bin/env python3
import os
import time
import threading
import smtplib
import email
import email.mime.multipart
import email.mime.text


class MailQueue:
  def __init__(self, maildir, faildir, server, port, username, password, sender, retries, timeout):
    self.maildir = maildir
    self.faildir = faildir
    self.server = server
    self.port = port
    self.username = username
    self.password = password
    self.sender = sender
    self.retries = retries
    self.timeout = timeout

    self.ml_retries = {}

    self.setup_smtp()

    threading.Thread(target=self.worker).start()

  def setup_smtp(self):
    self.smtp = smtplib.SMTP_SSL(self.server, self.port)
    self.smtp.login(self.username, self.password)

  def send_smtp(self, to_addr, subject, msg, is_html=False):
    msg_root = email.mime.multipart.MIMEMultipart('alternative')
    msg_root['Subject'] = subject
    msg_root['From'] = self.sender
    msg_root['To'] = to_addr

    mimetype = 'html' if is_html else 'plain'
    msg_root.attach(email.mime.text.MIMEText(msg, mimetype))

    try:
      self.smtp.sendmail(self.sender, [to_addr], msg_root.as_string())
    except smtplib.SMTPException:
      print('Lost connection to smtp server, retrying')
      self.setup_smtp()
      self.smtp.sendmail(self.sender, [to_addr], msg_root.as_string())

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
            print(f'{ml}/{self.ml_retries[ml]} failed: {type(e)}: {e}')

            if self.ml_retries[ml] >= int(self.retries):
              print(f'{ml} permanently failed')
              os.rename(mail_path, mail_path.replace(self.maildir, self.faildir))
              del self.ml_retries[ml]

      time.sleep(int(self.timeout))


if __name__ == '__main__':
  maildir = os.getenv('MAILDIR', '/maildir')
  faildir = os.getenv('FAILDIR', '/faildir')
  server = os.environ['SERVER']
  port = int(os.environ['PORT'])
  username = os.environ['USERNAME']
  password = os.environ['PASSWORD']
  sender = os.environ['SENDER']
  retries = int(os.getenv('RETRIES', 5))
  timeout = int(os.getenv('TIMEOUT', 60))

  if 'UMASK' in os.environ:
    os.umask(int(os.environ['UMASK'], 8))

  MailQueue(maildir, faildir, server, port, username, password, sender, retries, timeout)
