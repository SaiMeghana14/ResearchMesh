import requests

# Slack
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/your/webhook/url"
def send_to_slack(message):
    if not message: return
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

# Notion (mock)
NOTION_API_KEY = "your-notion-api-key"
NOTION_PAGE_ID = "your-page-id"
def send_to_notion(message):
    print(f"[Notion] Would send: {message}")

# GitHub (mock)
def save_to_github(file_name, content):
    print(f"[GitHub] Would commit {file_name}")
