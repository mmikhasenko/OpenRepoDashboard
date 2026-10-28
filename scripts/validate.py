import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
config = json.loads((root/'config/repositories.json').read_text())
data = json.loads((root/'site/data.json').read_text())
assert {r['repository'] for r in data['repositories']} == {r['repository'] for r in config['repositories']}
assert len(data['repositories']) == len(config['repositories'])
assert any(not r['errors'] for r in data['repositories']), 'All repository collections failed'
for path in (root/'site').rglob('*'):
    if path.is_file():
        assert path.name in {'index.html','style.css','app.js','data.json'}, f'Unexpected published file: {path.name}'
        content = path.read_text()
        for private_marker in ['/Users/', '/home/', 'ghp_', 'github_pat_', '-----BEGIN PRIVATE KEY']:
            assert private_marker not in content, f'Potential private data in {path.name}'
print('Public artifact validated')
