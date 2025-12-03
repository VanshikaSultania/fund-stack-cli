#========================
#FILE: report_service.py
#========================

import requests, json
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
console = Console()

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_report(transactions, budget_status, year, month):
    prompt = f"""
You are a financial analysis AI. Create a monthly report.
Month: {year}-{str(month).zfill(2)}
Transactions: {json.dumps(transactions, indent=2)}
Budgets: {json.dumps(budget_status, indent=2)}
Include:
- Income
- Expenses
- Overspending alerts
- Insights
- Recommendations
"""
    with Live(Spinner("dots","Generating AI Report..."), refresh_per_second=10):
        r = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json={"contents":[{"parts":[{"text":prompt}]}]})
    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Error generating report."