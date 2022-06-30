# zuul-alarm

Poll zuul job status for updates.

## Quickstart

### Install
After cloning the repository

```
$ pip install .
```

### Config
Copy example config provided in config.yaml.example to config.yaml

```
watchers:
  # Example script that calls notify-send on job update
  - type: shell
    cmd: ./contrib/notify.sh
# Zuul instances to poll
instances:
  - zuul.openstack.org
  - review.rdoproject.org/zuul
# Rules used to select jobs
rules:
  - name: Watch patch
    filters:
      patch: "845054"
    watched_fields:
      - start_time
      - result
```

Edit config to suit your needs

### run
```
$ zuul-alarm
```


## Example watchers
* `notify.sh`: Sends desktop notifications on events
* `pushover.sh`: Sends push notifications using pushover
