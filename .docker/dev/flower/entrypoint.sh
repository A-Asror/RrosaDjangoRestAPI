#!/bin/sh

celery -A core flower --loglevel=warning --port=9090
#--basic-auth=user1:password1,user2:password2
