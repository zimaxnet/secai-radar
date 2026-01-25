#!/usr/bin/env python3
"""
Script to create GitHub issues from backlog tickets.
Parses docs/backlog/mvp-build-tickets.md and creates issues via GitHub API.
"""

import re
import json
import subprocess
import time
from pathlib import Path

REPO = "zimaxnet/secai-radar"
PROJECT_NUMBER = 3

# Category mapping
CATEGORY_MAP = {
    "FE": "frontend",
    "BE": "backend",
    "DATA": "data",
    "PIPE": "pipeline",
    "SEC": "security",
    "DEVOPS": "devops",
    "UX": "ux"
}

def get_category_label(category_str):
    """Extract category label from category string (handles compound categories)."""
    # Handle compound categories like "FE/UX" or "BE/DEVOPS"
    categories = [c.strip() for c in category_str.split('/')]
    # Use the first category for the label
    primary_category = categories[0]
    return CATEGORY_MAP.get(primary_category, "frontend")  # Default to frontend

def parse_backlog_file(file_path):
    """Parse the backlog markdown file and extract ticket information."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tickets = []
    current_ticket = None
    
    # Pattern to match ticket headers
    ticket_pattern = r'^### (T-\d+) \((.+?)\) (.+)$'
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a ticket header
        match = re.match(ticket_pattern, line)
        if match:
            # Save previous ticket if exists
            if current_ticket:
                tickets.append(current_ticket)
            
            # Start new ticket
            ticket_id, category, title = match.groups()
            current_ticket = {
                'id': ticket_id,
                'category': category,
                'title': title,
                'status': 'pending',
                'priority': 'P0',
                'phase': 0,
                'description': '',
                'acceptance_criteria': [],
                'dependencies': 'none',
                'estimated_effort': '',
                'notes': '',
                'endpoint': ''
            }
            i += 1
            continue
        
        if current_ticket:
            # Parse ticket fields
            if line.startswith('**Status:**'):
                status_match = re.search(r'\*\*Status:\*\* (.+)', line)
                if status_match:
                    status = status_match.group(1).strip()
                    if '✅' in status or 'Completed' in status:
                        current_ticket['status'] = 'completed'
                    elif '🔄' in status or 'Partial' in status:
                        current_ticket['status'] = 'partial'
            
            elif line.startswith('**Priority:**'):
                priority_match = re.search(r'\*\*Priority:\*\* (.+)', line)
                if priority_match:
                    current_ticket['priority'] = priority_match.group(1).strip()
            
            elif line.startswith('**Description:**'):
                desc = line.replace('**Description:**', '').strip()
                if desc:
                    current_ticket['description'] = desc
            
            elif line.startswith('**Endpoint:**'):
                endpoint = line.replace('**Endpoint:**', '').strip()
                if endpoint:
                    current_ticket['endpoint'] = endpoint
            
            elif line.startswith('**Dependencies:**'):
                deps = line.replace('**Dependencies:**', '').strip()
                if deps and deps != 'none':
                    current_ticket['dependencies'] = deps
            
            elif line.startswith('**Estimated Effort:**'):
                effort = line.replace('**Estimated Effort:**', '').strip()
                if effort:
                    current_ticket['estimated_effort'] = effort
            
            elif line.startswith('**Notes:**'):
                notes = line.replace('**Notes:**', '').strip()
                if notes:
                    current_ticket['notes'] = notes
            
            elif line.startswith('**Acceptance criteria:**'):
                # Collect acceptance criteria
                i += 1
                while i < len(lines) and lines[i].strip().startswith('- ['):
                    criteria = lines[i].strip()
                    current_ticket['acceptance_criteria'].append(criteria)
                    i += 1
                continue
            
            # Determine phase from section headers
            if '## Phase 0' in line:
                current_ticket['phase'] = 0
            elif '## Phase 1' in line:
                current_ticket['phase'] = 1
            elif '## Phase 2' in line:
                current_ticket['phase'] = 2
            elif '## Phase 3' in line:
                current_ticket['phase'] = 3
            elif '## Phase 4' in line:
                current_ticket['phase'] = 4
            elif '## Optional' in line or '## Post-MVP' in line:
                current_ticket['phase'] = 5  # Post-MVP
        
        i += 1
    
    # Add last ticket
    if current_ticket:
        tickets.append(current_ticket)
    
    return tickets

def create_milestones():
    """Create GitHub milestones."""
    milestones = [
        ("Phase 0: Foundation", "Monorepo, CI/CD, Infrastructure", "2026-01-25"),
        ("Phase 1: Public MVP", "Database, API, Frontend Integration", "2026-01-30"),
        ("Phase 2: Automation", "Pipeline Workers", "2026-02-06"),
        ("Phase 3: Private Registry", "Auth, RBAC, Registry API/UI", "2026-02-13"),
        ("Phase 4: Graph + Hardening", "Graph Explorer, Security, Observability", "2026-02-20"),
        ("MVP Launch", "Production MVP launch", "2026-02-20"),
    ]
    
    print("Creating milestones...")
    for title, description, due_date in milestones:
        try:
            subprocess.run([
                'gh', 'api', f'repos/{REPO}/milestones',
                '-X', 'POST',
                '-f', f'title={title}',
                '-f', f'description={description}',
                '-f', f'due_on={due_date}T00:00:00Z'
            ], check=False, capture_output=True)
            print(f"  ✓ {title}")
        except Exception as e:
            print(f"  ✗ {title}: {e}")
    
    time.sleep(1)

def create_issue(ticket):
    """Create a GitHub issue from a ticket dictionary."""
    # Build title
    title = f"{ticket['id']}: {ticket['title']}"
    
    # Build labels
    category_label = f"category:{get_category_label(ticket['category'])}"
    priority_label = f"priority:{ticket['priority'].lower()}"
    phase_label = f"phase:{ticket['phase']}"
    
    labels = [category_label, priority_label, phase_label]
    if ticket['status'] == 'completed':
        labels.append('status:completed')
    elif ticket['status'] == 'partial':
        labels.append('status:partial')
    
    # Build milestone
    milestone_map = {
        0: "Phase 0: Foundation",
        1: "Phase 1: Public MVP",
        2: "Phase 2: Automation",
        3: "Phase 3: Private Registry",
        4: "Phase 4: Graph + Hardening",
    }
    milestone = milestone_map.get(ticket['phase'])
    
    # Build body
    body_parts = [f"## Description\n{ticket['description']}"]
    
    if ticket['endpoint']:
        body_parts.append(f"**Endpoint:** {ticket['endpoint']}")
    
    if ticket['dependencies'] and ticket['dependencies'] != 'none':
        body_parts.append(f"## Dependencies\n{ticket['dependencies']}")
    
    if ticket['acceptance_criteria']:
        body_parts.append("## Acceptance Criteria")
        body_parts.extend(ticket['acceptance_criteria'])
    
    if ticket['estimated_effort']:
        body_parts.append(f"## Estimated Effort\n{ticket['estimated_effort']}")
    
    if ticket['notes']:
        body_parts.append(f"## Notes\n{ticket['notes']}")
    
    body_parts.append(f"## References\n- Backlog Ticket: {ticket['id']}\n- Related Docs: [docs/backlog/mvp-build-tickets.md](docs/backlog/mvp-build-tickets.md)")
    
    body = '\n\n'.join(body_parts)
    
    # Create issue
    cmd = [
        'gh', 'issue', 'create',
        '--repo', REPO,
        '--title', title,
        '--body', body,
        '--label', ','.join(labels)
    ]
    
    if milestone:
        cmd.extend(['--milestone', milestone])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        issue_number = issue_url.split('/')[-1]
        
        # Add to project
        subprocess.run([
            'gh', 'project', 'item-add', str(PROJECT_NUMBER),
            '--owner', 'zimaxnet',
            '--url', issue_url
        ], capture_output=True, check=False)
        
        # Close if completed
        if ticket['status'] == 'completed':
            subprocess.run([
                'gh', 'issue', 'close', issue_number,
                '--repo', REPO,
                '--comment', 'This ticket was already completed during the planning phase.'
            ], capture_output=True, check=False)
        
        print(f"  ✓ Created {ticket['id']}: {title} (#{issue_number})")
        return issue_number
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to create {ticket['id']}: {e.stderr}")
        return None

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    backlog_file = repo_root / 'docs' / 'backlog' / 'mvp-build-tickets.md'
    
    if not backlog_file.exists():
        print(f"Error: Backlog file not found at {backlog_file}")
        return
    
    print("Parsing backlog file...")
    tickets = parse_backlog_file(backlog_file)
    print(f"Found {len(tickets)} tickets")
    
    # Create milestones
    create_milestones()
    
    # Create issues
    print("\nCreating issues...")
    created = 0
    for ticket in tickets:
        create_issue(ticket)
        created += 1
        time.sleep(1)  # Rate limiting
    
    print(f"\n✓ Created {created} issues")

if __name__ == '__main__':
    main()
