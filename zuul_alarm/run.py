from zuul_alarm.config import load_config
from zuul_alarm import RuleTracker, poll
import asyncio

def run():
    config = load_config('./config.yaml')

    trackers = [RuleTracker(r) for r in config.rules]
    asyncio.run(poll(config, trackers))


if __name__ == '__main__':
    run()
