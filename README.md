# MailQueue
File based emailing, simply drop a file with some text in a folder, that's it.

## Install instructions
Tested with Debian 10, will probably also work with other debian based systems.

* Modify `config.ini`, set SMTP variables to own mailserver
* Prerequisite: `apt install pipenv`
* Run `./install.sh`
* Start service `systemctl start mailqueue`
* (Optional) start at boot `systemctl enable mailqueue`
* Start sending emails `echo -e "me@example.com\ntestsubject\ntestbody" > maildir/testmailfile`
