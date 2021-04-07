#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

pipenv install

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cp mailqueue.service /etc/systemd/system/mailqueue.service
chown root:root /etc/systemd/system/mailqueue.service

sed -i "s#<WORKING_DIR>#"$SCRIPTPATH"#g" /etc/systemd/system/mailqueue.service
sed -i "s#<PIPENV_PATH>#"$(which pipenv)"#g" /etc/systemd/system/mailqueue.service

echo "Installed, to start run 'systemctl start mailqueue.service'"
