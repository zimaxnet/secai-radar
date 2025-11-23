
import json
import azure.functions as func
from pathlib import Path
from shared.utils import json_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    seeds_path = Path(__file__).resolve().parents[1] / "seeds_vendor_tools.json"
    data = json.loads(seeds_path.read_text())
    return func.HttpResponse(**json_response(data))
