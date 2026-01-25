#!/bin/bash

# Create GitHub labels for the project

REPO="zimaxnet/secai-radar"

# Category labels
gh label create "category:frontend" --repo "$REPO" --description "Frontend work" --color "0E8A16" 2>/dev/null || true
gh label create "category:backend" --repo "$REPO" --description "Backend/API work" --color "1D76DB" 2>/dev/null || true
gh label create "category:data" --repo "$REPO" --description "Data/Database work" --color "B60205" 2>/dev/null || true
gh label create "category:pipeline" --repo "$REPO" --description "Pipeline/Agents work" --color "5319E7" 2>/dev/null || true
gh label create "category:security" --repo "$REPO" --description "Security work" --color "D93F0B" 2>/dev/null || true
gh label create "category:devops" --repo "$REPO" --description "CI/CD/Infrastructure work" --color "FBCA04" 2>/dev/null || true
gh label create "category:ux" --repo "$REPO" --description "Copy/Docs/Design work" --color "C2E0C6" 2>/dev/null || true

# Priority labels
gh label create "priority:p0" --repo "$REPO" --description "Critical - must have for MVP" --color "B60205" 2>/dev/null || true
gh label create "priority:p1" --repo "$REPO" --description "High - important for MVP" --color "FBCA04" 2>/dev/null || true
gh label create "priority:p2" --repo "$REPO" --description "Nice to have - post-MVP" --color "0E8A16" 2>/dev/null || true

# Phase labels
gh label create "phase:0" --repo "$REPO" --description "Phase 0: Foundation" --color "7057FF" 2>/dev/null || true
gh label create "phase:1" --repo "$REPO" --description "Phase 1: Public MVP" --color "008672" 2>/dev/null || true
gh label create "phase:2" --repo "$REPO" --description "Phase 2: Automation" --color "1D76DB" 2>/dev/null || true
gh label create "phase:3" --repo "$REPO" --description "Phase 3: Private Registry" --color "B60205" 2>/dev/null || true
gh label create "phase:4" --repo "$REPO" --description "Phase 4: Graph + Hardening" --color "FBCA04" 2>/dev/null || true
gh label create "phase:post-mvp" --repo "$REPO" --description "Post-MVP features" --color "C2E0C6" 2>/dev/null || true

# Status labels
gh label create "status:completed" --repo "$REPO" --description "Already completed" --color "0E8A16" 2>/dev/null || true
gh label create "status:partial" --repo "$REPO" --description "Partially complete" --color "FBCA04" 2>/dev/null || true
gh label create "status:blocked" --repo "$REPO" --description "Blocked by dependencies" --color "B60205" 2>/dev/null || true

echo "Labels created successfully!"
