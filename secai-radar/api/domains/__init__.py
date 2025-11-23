
import json
import azure.functions as func
from pathlib import Path
from shared.utils import json_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    seeds_path = Path(__file__).resolve().parents[1] / "seeds_domain_codes.json"
    data = json.loads(seeds_path.read_text())
    items = [{"code": k, "name": v} for k,v in data.items()]
    return func.HttpResponse(**json_response(items))
