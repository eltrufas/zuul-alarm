import logging
from zuul_alarm.config import Config, Rule

import aiohttp

def enhance_list(jobs, parent, fields):
    for job in jobs:
        for k, v in fields.items():
            job[v] = parent[k]

def identity_dict(*args):
    return {a: a for a in args}

def process_pipeline(pipeline):
    queues = pipeline['change_queues']
    jobs = [process_queue(q) for q in queues]
    jobs = [x for sublist in jobs for x in sublist]
    enhance_list(jobs, pipeline, {'name': 'pipeline_name'})
    return jobs


def process_queue(queue):
    heads = [h for sublist in queue['heads'] for h in sublist]
    jobs = [process_head(h) for h in heads]
    jobs = [x for sublist in jobs for x in sublist]
    enhance_list(jobs, queue, {'name': 'queue_name'})
    return jobs

def process_head(head):
    patch = None
    revision = None
    if head['id'] is not None:
        head_id  = head['id'].split(',')
        if len(head_id) == 2:
            patch, revision = head_id
    head['patch'] = patch
    head['revision'] = revision

    jobs = head['jobs']

    head_fields = identity_dict('owner', 'project', 'project_canonical',
                                'patch', 'revision')
    head_fields['id'] = 'head_id'

    enhance_list(jobs, head, head_fields)
    return jobs

def process_res(res):
    jobs = [process_pipeline(p) for p in res['pipelines']]
    jobs = [x for sublist in jobs for x in sublist]
    return jobs


def build_status_url(instance):
    return f'https://{instance}/api/status'



class Poller:
    config: Config
    http: aiohttp.ClientSession
    def __init__(self, config: Config, http: aiohttp.ClientSession):
        self.config = config
        self.http = http

    async def poll_zuul(self) -> list[dict]:
        instances = self.config.instances
        jobs = []
        for instance in instances:
            instance_jobs = await self.poll_instance(instance)
            jobs.extend(instance_jobs)
        return jobs

    async def poll_instance(self, instance: str) -> list[dict]:
        logging.info(f'polling instance {instance}')
        status_url = build_status_url(instance)
        res = await self.http.get(status_url)
        logging.debug(f'{instance} responded with {res.status}')
        resjson = await res.json()
        jobs =  process_res(resjson)
        return jobs

