"""
report_service.py
Generates monthly financial report using Gemini AI API.
"""

import requests
import json

GEMINI_API_KEY = "AIzaSyDzGaS9lraFz2eho80Mb8ssHP_vhmiLSj0"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_report(transactions, budget_status, year, month):
    """Send data to Gemini model and get a smart financial report."""

    prompt = f"""
You are a financial analysis AI. Create a clean, structured monthly report.

MONTH: {year}-{str(month).zfill(2)}

### TRANSACTIONS ###
{json.dumps(transactions, indent=2)}

### BUDGET STATUS ###
{json.dumps(budget_status, indent=2)}

Provide:
- Total income
- Total expenses
- Top spending categories
- Overspending alerts
- Savings insights
- Recommendations for next month
- Write in simple, friendly language.
"""

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    r = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json=data
    )

    reply = r.json()
    
    try:
        return reply["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Error generating report."
