# SecAI Radar — GitHub Issue Templates (v1)
Generated: 2026-01-23

## What this gives you
Issue Forms optimized for **Cursor / VS Code / Antigravity**:
- Feature / Endpoint / Service
- Task / Chore
- Bug
- Spike / Research
- Epic

## Installation
Copy the `.github/ISSUE_TEMPLATE/` folder into the root of your GitHub repo:

```
<repo-root>/
  .github/
    ISSUE_TEMPLATE/
      config.yml
      feature.yml
      task.yml
      bug.yml
      spike.yml
      epic.yml
```

Commit to `main`, and GitHub will automatically use these forms.

## Suggested labels
Create these labels (optional but helpful):
- type:feature, type:task, type:bug, type:spike, type:epic
- phase:0, phase:1, phase:2, phase:3, phase:4
- priority:P0, priority:P1, priority:P2
- service:public-web, service:public-api, service:private-web, service:private-api, service:workers, service:publisher, service:graph

## Workflow rule (keeps everything synced)
- Each checkbox in your P0/P1 checklist becomes an Issue.
- Every PR closes at least one issue and updates your refactoring progress doc (one line).

