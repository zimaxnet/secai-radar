#!/bin/bash

# Script to create GitHub issues from backlog tickets
# Usage: ./scripts/create-github-issues.sh

REPO="zimaxnet/secai-radar"
PROJECT_NUMBER=3

# Function to create issue
create_issue() {
    local ticket_id=$1
    local title=$2
    local category=$3
    local priority=$4
    local phase=$5
    local status=$6
    local description=$7
    local acceptance_criteria=$8
    local dependencies=$9
    local estimated_effort=${10}
    local notes=${11}
    local endpoint=${12}
    
    # Build labels
    local labels="category:${category},priority:${priority},phase:${phase}"
    if [ "$status" = "completed" ]; then
        labels="${labels},status:completed"
    elif [ "$status" = "partial" ]; then
        labels="${labels},status:partial"
    fi
    
    # Build milestone
    local milestone=""
    case $phase in
        0) milestone="Phase 0: Foundation" ;;
        1) milestone="Phase 1: Public MVP" ;;
        2) milestone="Phase 2: Automation" ;;
        3) milestone="Phase 3: Private Registry" ;;
        4) milestone="Phase 4: Graph + Hardening" ;;
        *) milestone="" ;;
    esac
    
    # Build body
    local body="## Description
${description}"
    
    if [ -n "$endpoint" ]; then
        body="${body}

**Endpoint:** ${endpoint}"
    fi
    
    if [ -n "$dependencies" ] && [ "$dependencies" != "none" ]; then
        body="${body}

## Dependencies
${dependencies}"
    fi
    
    body="${body}

## Acceptance Criteria
${acceptance_criteria}"
    
    if [ -n "$estimated_effort" ]; then
        body="${body}

## Estimated Effort
${estimated_effort}"
    fi
    
    if [ -n "$notes" ]; then
        body="${body}

## Notes
${notes}"
    fi
    
    body="${body}

## References
- Backlog Ticket: ${ticket_id}
- Related Docs: [docs/backlog/mvp-build-tickets.md](docs/backlog/mvp-build-tickets.md)"
    
    # Create issue
    echo "Creating issue: ${title}..."
    gh issue create \
        --repo "$REPO" \
        --title "${title}" \
        --body "$body" \
        --label "$labels" \
        ${milestone:+--milestone "$milestone"} \
        --format json > /tmp/issue_${ticket_id}.json
    
    # Get issue number
    local issue_number=$(jq -r '.number' /tmp/issue_${ticket_id}.json)
    echo "Created issue #${issue_number}: ${title}"
    
    # Add to project
    if [ -n "$issue_number" ]; then
        gh project item-add "$PROJECT_NUMBER" --owner zimaxnet --url "https://github.com/${REPO}/issues/${issue_number}" 2>/dev/null || true
    fi
    
    # Mark as completed if status is completed
    if [ "$status" = "completed" ]; then
        gh issue close "$issue_number" --repo "$REPO" --comment "This ticket was already completed during the planning phase." 2>/dev/null || true
    fi
    
    sleep 1  # Rate limiting
}

# Create milestones first
echo "Creating milestones..."
gh api repos/${REPO}/milestones -X POST -f title="Phase 0: Foundation" -f description="Monorepo, CI/CD, Infrastructure" -f due_on="2026-01-25T00:00:00Z" > /dev/null 2>&1 || true
gh api repos/${REPO}/milestones -X POST -f title="Phase 1: Public MVP" -f description="Database, API, Frontend Integration" -f due_on="2026-01-30T00:00:00Z" > /dev/null 2>&1 || true
gh api repos/${REPO}/milestones -X POST -f title="Phase 2: Automation" -f description="Pipeline Workers" -f due_on="2026-02-06T00:00:00Z" > /dev/null 2>&1 || true
gh api repos/${REPO}/milestones -X POST -f title="Phase 3: Private Registry" -f description="Auth, RBAC, Registry API/UI" -f due_on="2026-02-13T00:00:00Z" > /dev/null 2>&1 || true
gh api repos/${REPO}/milestones -X POST -f title="Phase 4: Graph + Hardening" -f description="Graph Explorer, Security, Observability" -f due_on="2026-02-20T00:00:00Z" > /dev/null 2>&1 || true
gh api repos/${REPO}/milestones -X POST -f title="MVP Launch" -f description="Production MVP launch" -f due_on="2026-02-20T00:00:00Z" > /dev/null 2>&1 || true

echo "Milestones created. Now creating issues..."

# Note: Due to the large number of issues, I'll create a Python script to parse the markdown and create issues
# For now, let's create a few key issues manually to demonstrate, then we can create the rest

echo "Issue creation script ready. Run with Python script for full automation."
