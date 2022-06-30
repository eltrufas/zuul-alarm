from zuul_alarm.config import Rule, FieldDiff
import logging

logger = logging.getLogger('tracker')

def match_rule(job: dict, rule: Rule):
    return all(job[k] == v for k, v in rule.filters.items())

def build_job_id(job: dict) -> str:
    els = (job['pipeline_name'], job['head_id'], job['name'])
    els = tuple(e for e in els if e is not None)
    job_id = '/'.join(els)
    return job_id

class RuleTracker:
    jobs: dict[str, dict]
    rule: Rule

    def __init__(self, rule: Rule):
        self.rule = rule
        self.jobs = {}


    def update(self, update: list[dict]) -> list[tuple[list[FieldDiff], dict]]:
        selected = [j for j in update if match_rule(j, self.rule)]
        current_uuids = set(self.jobs.keys())
        update_dict = {build_job_id(job): job for job in selected}
        updated_uuids = set(update_dict.keys())
        new_uuids = updated_uuids - current_uuids

        updated = []

        for uuid in current_uuids.intersection(updated_uuids):
            current = self.jobs[uuid]
            new = update_dict[uuid]
            diffs = []
            for field in self.rule.watched_fields:
                if field not in new:
                    logger.warning(f"{self.rule.name}: field \"{field}\" missing from job")
                    continue

                if current[field] != new[field]:
                    diff = FieldDiff(field=field, old=current[field],
                                    new=new[field])
                    diffs.append(diff)
            current.update(new)
            if diffs:
                updated.append((diffs, new))

        updated.extend(([], update_dict[uuid]) for uuid in new_uuids)
        self.jobs.update({uuid: update_dict[uuid] for uuid in new_uuids})
        for uuid in current_uuids - updated_uuids:
            self.jobs.pop(uuid)
        return updated
