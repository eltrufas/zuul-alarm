#!/bin/sh

TITLE=$ZUUL_JOB_name

if [ $ZUUL_EVENT == new ]; then
  MSG="started tracking job"
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

notify-send "$TITLE" "$MSG"

