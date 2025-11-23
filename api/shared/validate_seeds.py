import json
from pathlib import Path
import fastjsonschema

ROOT = Path(__file__).resolve().parents[2]
SEEDS_DIR = ROOT / 'seeds'
SCHEMAS_DIR = SEEDS_DIR / 'schemas'
API_DIR = ROOT / 'api'

SCHEMAS = {
    'control_requirements': SCHEMAS_DIR / 'control_requirements.schema.json',
    'tool_capabilities': SCHEMAS_DIR / 'tool_capabilities.schema.json',
    'vendor_tools': SCHEMAS_DIR / 'vendor_tools.schema.json',
}

TARGETS = {
    'control_requirements': [SEEDS_DIR / 'control_requirements.json', API_DIR / 'seeds_control_requirements.json'],
    'tool_capabilities': [SEEDS_DIR / 'tool_capabilities.json', API_DIR / 'seeds_tool_capabilities.json'],
    'vendor_tools': [SEEDS_DIR / 'vendor_tools.json', API_DIR / 'seeds_vendor_tools.json'],
}

def load_json(p: Path):
    return json.loads(p.read_text())

def validate_all() -> int:
    errors = []
    for name, schema_path in SCHEMAS.items():
        schema = load_json(schema_path)
        validate = fastjsonschema.compile(schema)
        for target in TARGETS[name]:
            if not target.exists():
                continue
            try:
                data = load_json(target)
                validate(data)
                print(f"OK: {target}")
            except Exception as e:
                errors.append((str(target), str(e)))
                print(f"FAIL: {target}: {e}")
    return 1 if errors else 0

if __name__ == '__main__':
    exit(validate_all())
