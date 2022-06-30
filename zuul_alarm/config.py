from pydantic import BaseModel
import pyinotify
from typing import Optional, Literal, Any
import yaml
import asyncio
import logging
import os

logger = logging.getLogger('config')

class FieldDiff(BaseModel):
    field: str
    old: Any
    new: Any

class ShellWatcher(BaseModel):
    type: Literal['shell']
    cmd: str
    async def handle_event(self, diff: Optional[FieldDiff], job: dict):
        env = os.environ.copy()

        env.update({f'ZUUL_JOB_{k}': str(v) or '' for k, v in job.items()})
        if diff is None:
            env['ZUUL_EVENT'] = 'new'
        else:
            env['ZUUL_EVENT'] = 'change'
            env['ZUUL_DIFF_FIELD'] = str(diff.field)
            env['ZUUL_DIFF_OLD'] = str(diff.old)
            env['ZUUL_DIFF_NEW'] = str(diff.new)
        await self.run(env)

    async def run(self, env):
        proc = await asyncio.create_subprocess_shell(self.cmd, env=env)
        await proc.wait()


class Rule(BaseModel):
    name: str
    filters: dict
    watched_fields: list[str]


class Config(BaseModel):
    instances: list[str]
    rules: list[Rule]
    watchers: list[ShellWatcher]


def load_config(path: str):
    raw_config = None
    with open(path) as fp:
        raw_config = yaml.safe_load(fp)
    return Config(**raw_config)

