#!/bin/bash

if [ ! -f /mnt/config_bili.ini ]; then
  echo 'Error: /mnt/config_bili.ini file not found. Please mount the /mnt/config_bili.ini file and try again.'
  exit 1
fi

cp -f /mnt/config_bili.ini /app/config_bili.ini
python -u main.py
