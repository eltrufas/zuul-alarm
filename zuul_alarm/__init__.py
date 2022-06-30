import logging, asyncio
from zuul_alarm.config import Config
from zuul_alarm.poller import Poller
from zuul_alarm.tracker import RuleTracker, build_job_id

import aiohttp

logger = logging.getLogger('poller')
logger.setLevel(logging.DEBUG)

def handle_update(tracker, watchers, diffs, job):
    loop = asyncio.get_running_loop()
    job_id = build_job_id(job)
    for diff in diffs:
        logger.info(
            f"{job_id}: rule {tracker} detected change for job {diff}")
        for watcher in watchers:
            loop.create_task(watcher.handle_event(diff, job))
    if not diffs:
        logger.info(
            f"rule {tracker} detected new job {build_job_id(job)}")
        for watcher in watchers:
            loop.create_task(watcher.handle_event(None, job))


async def poll(config: Config, trackers: list[RuleTracker]):
    async with aiohttp.ClientSession() as session:
        poller = Poller(config, session)


        while True:
            logger.debug("polling zuul")
            jobs = await poller.poll_zuul()
            updates = {tracker.rule.name: tracker.update(jobs)
                       for tracker in trackers}
            for t in updates:
                for diffs, job in updates[t]:
                    handle_update(t, config.watchers, diffs, job)
            await asyncio.sleep(5)
