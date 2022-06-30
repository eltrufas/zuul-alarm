#!/bin/bash

PUSHOVER_ENDPOINT=https://api.pushover.net/1/messages.json

TITLE=$ZUUL_JOB_name

if [ $ZUUL_EVENT == new ]; then
    MSG="started tracking job"
    exit 0
else
    MSG="$ZUUL_DIFF_FIELD changed to: $ZUUL_DIFF_NEW"
    case $ZUUL_DIFF_FIELD in
      result)
        MSG="Job result: $ZUUL_DIFF_NEW"
        ;;
      start_time)
        MSG="Job started"
        ;;
    esac
fi

curl -s \
  --form-string "token=$PUSHOVER_TOKEN" \
  --form-string "user=$PUSHOVER_USER" \
  --form-string "title=$TITLE" \
  --form-string "message=$MSG" \
  https://api.pushover.net/1/messages.json

