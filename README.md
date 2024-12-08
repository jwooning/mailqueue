# MailQueue
File based emailing, simply drop a file with some text in a folder, that's it.

## Install instructions
Tested with Debian 10, will probably also work with other debian based systems.

* Modify `docker-compose.yml`
  * Setup `user`
  * Create correct volumes
  * Set SMTP variables to own mailserver
* Start with `docker compose up`
* Start sending emails `echo -e "me@example.com\ntestsubject\ntestbody" > ~/maildir/testmailfile`
