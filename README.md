# MailQueue

## Install instructions
Tested with Debian 10, will probably also work with other debian based systems.

* Modify `config.ini`, set SMTP variables to own mailserver
* Prerequisite: `apt install pipenv`
* Run `./install.sh`
* Start service `systemctl start mailqueue`
* (Optional) start at boot `systemctl enable mailqueue`
