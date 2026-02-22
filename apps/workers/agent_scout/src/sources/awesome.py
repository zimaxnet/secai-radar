import requests
import re
from typing import List, Dict, Any

def fetch_awesome_copilot_agents() -> List[Dict[str, Any]]:
    """
    Scrape the awesome-copilot markdown README to extract agent repositories.
    """
    url = "https://raw.githubusercontent.com/copilot-extensions/awesome-copilot/main/README.md"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text
        
        observations = []
        # Find all markdown links that look like GitHub repos
        pattern = r"\[(.*?)\]\((https://github\.com/[^/]+/[^/]+)/?\)"
        matches = re.findall(pattern, content)
        
        for name, repo_url in matches:
            if "copilot-extensions/awesome-copilot" in repo_url:
                continue
                
            obs = {
                "name": name.strip(),
                "github_url": repo_url.strip(),
                "source": "awesome-copilot",
                "integration_type": "agent",
                "agent_type": "Copilot Extension"
            }
            observations.append(obs)
            
        return observations
    except Exception as e:
        print(f"Error fetching awesome-copilot: {e}")
        return []
