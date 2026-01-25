# Ticket Template

Use this template when creating new tickets or converting tickets to issues.

```markdown
### T-XXX (CATEGORY) Ticket Title
**Status:** ⏳ Pending  
**Priority:** P0  
**Phase:** Phase X  
**Assignee:** [Optional]  
**Sprint:** [Optional]  

**Description:** [Brief description of what needs to be done]

**Dependencies:** T-XXX, T-YYY  
**Blocks:** T-XXX, T-YYY  

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Estimated Effort:** X hours  
**Actual Effort:** [Fill after completion]

**Technical Notes:**
- [Any technical considerations]
- [Related files/components]
- [Design decisions]

**Testing:**
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Manual testing completed
- [ ] Code review completed

**Related:**
- Related tickets: T-XXX, T-YYY
- Related docs: [links]
- Related PRs: [links]
```

## Categories

- **FE**: Frontend
- **BE**: Backend/API
- **DATA**: Data/Database
- **PIPE**: Pipeline/Agents
- **SEC**: Security
- **DEVOPS**: CI/CD/Infrastructure
- **UX**: Copy/Docs/Design

## Priority Levels

- **P0**: Critical (must have for MVP)
- **P1**: High (important for MVP)
- **P2**: Nice to have (post-MVP)

## Status Values

- ⏳ Pending / Not Started
- 🔄 In Progress / Partial
- ✅ Completed
- 🚫 Blocked
- ❌ Cancelled
