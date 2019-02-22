#!/usr/bin/bash
apt update
apt upgrade -y
apt install -y python3 python3-pip virtualenv git
mkdir /opt/domino
cd /opt/domino
virtualenv --python=python3 env
. /opt/domino/env/bin/activate
pip3 install django channels celery django-celery-beat redis