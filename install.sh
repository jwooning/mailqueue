#!/bin/bash

pipenv install

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cp mailqueue.service .mailqueue.service

sed -i "s#<USER>#"$(id -u -n)"#g" .mailqueue.service
sed -i "s#<GROUP>#"$(id -g -n)"#g" .mailqueue.service
sed -i "s#<WORKING_DIR>#"$SCRIPTPATH"#g" .mailqueue.service
sed -i "s#<PIPENV_PATH>#"$(which pipenv)"#g" .mailqueue.service

sudo mv .mailqueue.service /etc/systemd/system/mailqueue.service
sudo chown root:root /etc/systemd/system/mailqueue.service

echo "Installed, to start run 'systemctl start mailqueue.service'"
