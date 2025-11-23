# GitHub Actions Workflow Notifications

## Overview

There are several ways to receive notifications when GitHub Actions workflows fail:

1. **GitHub's Built-in Notifications** (Email/Web)
2. **Slack Notifications**
3. **Microsoft Teams Notifications**
4. **Email Notifications** (via SMTP)
5. **Custom Actions** (Discord, PagerDuty, etc.)

---

## Method 1: GitHub Built-in Notifications (Easiest)

### Setup

1. Go to: https://github.com/settings/notifications
2. Scroll to **"Actions"** section
3. Enable:
   - ✅ **Email** notifications for workflow runs
   - ✅ **Web** notifications
4. Optionally, select **"Only failed workflows"** to reduce noise

### What You'll Receive

- Email notifications when workflows fail
- Web notifications in GitHub UI
- Notifications for workflows you trigger or are watching

**Pros**: No code changes needed, works immediately  
**Cons**: Only email/web, no integrations with Slack/Teams

---

## Method 2: Slack Notifications (Recommended)

### Prerequisites

1. Create a Slack Incoming Webhook:
   - Go to: https://api.slack.com/apps
   - Create a new app or use existing
   - Add "Incoming Webhooks" feature
   - Create webhook for your channel
   - Copy webhook URL

2. Add to GitHub Secrets:
   - Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions
   - Add secret: `SLACK_WEBHOOK_URL` with your webhook URL

### Add to Workflows

Add this step to your workflows (after the deploy step):

```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: slackapi/slack-github-action@v1.27.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "❌ Workflow Failed: ${{ github.workflow }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*❌ Workflow Failed*\n*Workflow:* ${{ github.workflow }}\n*Branch:* ${{ github.ref_name }}\n*Commit:* <${{ github.event.head_commit.url }}|${{ github.event.head_commit.message }}>\n*Run:* <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
            }
          }
        ]
      }
```

---

## Method 3: Microsoft Teams Notifications

### Prerequisites

1. Create Teams Incoming Webhook:
   - In Teams, go to your channel → ... → Connectors
   - Add "Incoming Webhook"
   - Copy webhook URL

2. Add to GitHub Secrets:
   - Secret name: `TEAMS_WEBHOOK_URL`

### Add to Workflows

```yaml
- name: Notify Teams on Failure
  if: failure()
  uses: aliencube/microsoft-teams-actions@v0.8.0
  with:
    webhook_uri: ${{ secrets.TEAMS_WEBHOOK_URL }}
    title: "❌ Workflow Failed: ${{ github.workflow }}"
    summary: "Workflow run failed"
    text: |
      **Workflow:** ${{ github.workflow }}
      **Branch:** ${{ github.ref_name }}
      **Commit:** ${{ github.event.head_commit.message }}
      **Run:** ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

---

## Method 4: Email Notifications (via SMTP)

### Prerequisites

1. Get SMTP credentials (Gmail, Outlook, SendGrid, etc.)
2. Add to GitHub Secrets:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `EMAIL_TO` (recipient email)

### Add to Workflows

```yaml
- name: Send Email on Failure
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: ${{ secrets.SMTP_HOST }}
    server_port: ${{ secrets.SMTP_PORT }}
    username: ${{ secrets.SMTP_USER }}
    password: ${{ secrets.SMTP_PASSWORD }}
    subject: "❌ Workflow Failed: ${{ github.workflow }}"
    to: ${{ secrets.EMAIL_TO }}
    from: GitHub Actions
    body: |
      Workflow: ${{ github.workflow }}
      Branch: ${{ github.ref_name }}
      Commit: ${{ github.event.head_commit.message }}
      Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

---

## Method 5: Always Notify (Success + Failure)

To receive notifications for both success and failure:

```yaml
- name: Notify Slack
  if: always()  # Runs on success or failure
  uses: slackapi/slack-github-action@v1.27.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "${{ job.status == 'success' && '✅' || '❌' }} Workflow ${{ job.status == 'success' && 'Succeeded' || 'Failed' }}: ${{ github.workflow }}"
      }
```

---

## Recommended Implementation

For the SecAI Radar project, I recommend:

1. **Enable GitHub built-in notifications** (Method 1) - Quick setup, no code changes
2. **Add Slack notifications** (Method 2) - Team visibility, requires webhook setup

### Quick Start: Enable GitHub Notifications

1. Go to: https://github.com/settings/notifications
2. Under "Actions", enable:
   - ✅ Email notifications
   - ✅ "Only failed workflows" (optional, to reduce noise)
3. Done! You'll now receive emails when workflows fail.

### Adding Slack Notifications

1. **Create Slack Webhook**:
   - Go to: https://api.slack.com/apps
   - Create app → Add "Incoming Webhooks" → Create webhook
   - Copy webhook URL

2. **Add to GitHub Secrets**:
   - Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions
   - Click "New repository secret"
   - Name: `SLACK_WEBHOOK_URL`
   - Value: Your webhook URL
   - Click "Add secret"

3. **Update Workflows**:
   - See example workflows in `.github/workflows/`:
     - `azure-static-web-apps-with-notifications.yml.example`
     - `azure-functions-deploy-with-notifications.yml.example`
   - Copy the notification step to your existing workflows
   - Or rename the example files to replace the originals

---

## Notification Settings Links

- **GitHub Notifications**: https://github.com/settings/notifications
- **Repository Secrets**: https://github.com/zimaxnet/secai-radar/settings/secrets/actions
- **Repository Notifications**: https://github.com/zimaxnet/secai-radar/notifications

---

## Testing

To test notifications:
1. Add a step that intentionally fails: `run: exit 1`
2. Push to trigger workflow
3. Verify notification is received
4. Remove the test step

