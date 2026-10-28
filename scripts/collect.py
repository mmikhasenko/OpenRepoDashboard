"""Collect allowlisted public GitHub metadata; never read local checkout mappings."""
import concurrent.futures
import datetime as dt
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BAD = {'failure', 'timed_out', 'action_required', 'startup_failure'}

def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'OpenRepoDashboard', 'X-GitHub-Api-Version': '2022-11-28'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://api.github.com/' + path, headers=headers), timeout=40) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError('GitHub HTTP ' + str(error.code)) from None
        except (OSError, TimeoutError):
            if attempt == 2:
                raise RuntimeError('GitHub connection unavailable') from None
            time.sleep(2 ** attempt)

def pages(path, key=None):
    result = []
    for page in range(1, 101):
        data = api(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
        batch = data[key] if key else data
        result.extend(batch)
        if len(batch) < 100:
            return result
    raise RuntimeError('Pagination limit exceeded')

def duration(run):
    if run.get('status') != 'completed':
        return None
    try:
        return max(0, round((dt.datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00')) - dt.datetime.fromisoformat(run['run_started_at'].replace('Z', '+00:00'))).total_seconds()))
    except (KeyError, ValueError, TypeError):
        return None

def collect(item):
    name = item['repository']
    result = dict(item, url='https://github.com/' + name, workflows=[], issues=[], prs=[], errors=[])
    prefix = 'repos/' + name
    try:
        meta = api(prefix)
        if meta.get('private') or meta.get('visibility') != 'public':
            raise RuntimeError('Repository is not public; collection blocked')
        result.update(description=meta.get('description') or '', branch=meta['default_branch'], archived=meta['archived'])
    except Exception as error:
        result['errors'].append(str(error))
        return result
    try:
        for issue in pages(prefix + '/issues?state=open&sort=updated&direction=desc'):
            entry = {k: issue[k] for k in ('number', 'title', 'html_url', 'updated_at')}
            entry['author'] = issue['user']['login']
            entry['labels'] = [label['name'] for label in issue['labels']]
            result['prs' if 'pull_request' in issue else 'issues'].append(entry)
    except Exception as error:
        result['errors'].append('Issues / PRs: ' + str(error))
    try:
        workflows = pages(prefix + '/actions/workflows', 'workflows')
        branch = urllib.parse.quote(result['branch'], safe='')
        for workflow in workflows:
            row = {'name': workflow['name'], 'url': workflow['html_url'], 'state': workflow['state'], 'status': 'no_runs', 'duration': None}
            # Per-workflow lookup prevents frequent jobs hiding less frequent failures.
            runs = api(prefix + f'/actions/workflows/{workflow["id"]}/runs?branch={branch}&per_page=10')['workflow_runs']
            runs = [r for r in runs if r['event'] not in ('pull_request', 'pull_request_target')]
            if runs:
                run = runs[0]
                row.update(status=run['conclusion'] or run['status'], url=run['html_url'], date=run['updated_at'], duration=duration(run), event=run['event'])
            result['workflows'].append(row)
    except Exception as error:
        result['errors'].append('Workflows: ' + str(error))
    return result

def main():
    config = json.loads((ROOT / 'config/repositories.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        repos = list(pool.map(collect, config['repositories']))
    data = {'updated_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'categories': config['categories'], 'repositories': repos}
    target = ROOT / 'site/data.json'
    temp = target.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(target)
    print(f'Collected {len(repos)} repositories; {sum(bool(r["errors"]) for r in repos)} with incomplete data')

if __name__ == '__main__':
    main()
