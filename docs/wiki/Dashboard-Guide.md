---
layout: default
title: Dashboard Guide
---

# Dashboard Guide

Complete guide to understanding and using the SecAI Radar Dashboard.

---

## Overview

The Dashboard provides a comprehensive overview of your security posture, showing key metrics, domain breakdowns, and visual analytics.

---

## Key Metrics

### Overall Statistics Cards

Four primary metrics displayed at the top:

#### Total Controls
- **Purpose**: Shows total number of controls being assessed
- **Icon**: Document icon
- **Color**: Slate (neutral)
- **Use**: Baseline for understanding assessment scope

#### Complete
- **Purpose**: Number of controls marked as complete
- **Icon**: Checkmark icon
- **Color**: Green
- **Use**: Track compliance progress
- **Additional Info**: Shows overall compliance percentage

#### In Progress
- **Purpose**: Number of controls currently being worked on
- **Icon**: Clock icon
- **Color**: Yellow
- **Use**: Identify active work items

#### Not Started
- **Purpose**: Number of controls not yet started
- **Icon**: X icon
- **Color**: Red
- **Use**: Identify work backlog

---

## Domain Breakdown

### Domain Cards

Each security domain is displayed as a card showing:

#### Header Section
- **Domain Name**: Full domain name (e.g., "Network Security")
- **Compliance Badge**: Color-coded percentage badge
  - Green (≥80%): Good compliance
  - Yellow (50-79%): Fair compliance
  - Red (<50%): Poor compliance

#### Metrics Section
- **Complete**: Number and percentage of complete controls
- **In Progress**: Number of controls in progress
- **Not Started**: Number of controls not started

#### Progress Bar
- Visual representation of completion percentage
- Green bar showing progress toward 100%
- Updates in real-time as controls are updated

### Understanding Domain Cards

1. **Quick Assessment**: Glance at badges to see which domains need attention
2. **Detailed Review**: Click or expand cards for detailed metrics
3. **Progress Tracking**: Watch progress bars improve over time
4. **Comparison**: Compare domains to identify patterns

---

## Compliance Overview (Radar Chart)

### Radar Chart Visualization

Multi-series radar chart showing:

#### Series
- **Complete** (Green): Controls marked as complete
- **In Progress** (Yellow): Controls currently in progress
- **Not Started** (Red): Controls not yet started

#### Axes
- Each axis represents a security domain
- Distance from center indicates quantity
- Multiple series show distribution across statuses

### Using the Radar Chart

1. **Overall View**: See all domains at once
2. **Pattern Recognition**: Identify domains with similar patterns
3. **Progress Tracking**: Watch chart change as controls are updated
4. **Gap Analysis**: Identify domains with high "Not Started" values

### Interpreting the Chart

- **Balanced Shape**: All domains progressing evenly
- **Spiky Shape**: Some domains ahead, others behind
- **Small Center**: Many controls not started
- **Large Green**: Good compliance overall

---

## Loading States

### While Loading Data

- **Spinner**: Shows loading animation
- **Message**: "Loading..." text
- **Placeholder**: Content area reserved for data

### Empty States

- **No Data**: Message when no controls are configured
- **Help Text**: Guidance on next steps
- **Action Links**: Links to relevant pages (e.g., Import Controls)

---

## Best Practices

### 1. Regular Review
- Check dashboard daily/weekly for progress
- Track trends over time
- Identify domains needing attention

### 2. Set Goals
- Target compliance percentages (e.g., 80% complete)
- Set domain-specific goals
- Track progress toward goals

### 3. Prioritize Work
- Focus on domains with low compliance
- Address "Not Started" controls first
- Balance "In Progress" workload

### 4. Use for Reporting
- Export dashboard metrics for reports
- Share dashboard with stakeholders
- Use for executive briefings

---

## Troubleshooting

### No Data Showing
- **Check**: Controls have been imported
- **Check**: Tenant ID is correct
- **Action**: Import controls or check filters

### Metrics Not Updating
- **Check**: Controls have been updated recently
- **Check**: Browser cache (refresh page)
- **Action**: Refresh page or clear cache

### Chart Not Rendering
- **Check**: Browser supports SVG
- **Check**: JavaScript is enabled
- **Action**: Try different browser or update browser

---

## Tips

1. **Bookmark**: Bookmark dashboard for quick access
2. **Refresh**: Refresh page to get latest data
3. **Compare**: Compare current metrics to previous periods
4. **Export**: Take screenshots for documentation
5. **Share**: Share dashboard URL with team members

---

**Related Guides**: [Controls Guide](/wiki/Controls-Guide) | [Gaps Guide](/wiki/Gaps-Guide)
