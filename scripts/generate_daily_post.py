import os
import random
import re
import datetime
from pathlib import Path

# NOTE: This script is intended to be run in an environment with the ollama MCP tool available
# or by the AI agent itself. For the purpose of this demonstration, we'll implement the logic 
# and the agent will handle the AI completion step.

REPORTS_DIR = Path("Pilot_Reports")
OUTPUT_DIR = Path("daily_posts")
TEMPLATE_FILE = Path(__file__).parent.parent / "daily_post_template.md"

def get_random_report():
    sectors = [d for d in REPORTS_DIR.iterdir() if d.is_dir()]
    if not sectors:
        return None
    
    sector = random.choice(sectors)
    reports = list(sector.glob("*.md"))
    if not reports:
        return get_random_report() # Recursive fallback
    
    return random.choice(reports)

def parse_report(file_path):
    content = file_path.read_text(encoding="utf-8")
    
    # Simple regex extraction for metadata
    sector_match = re.search(r"\*\*板塊:\*\* (.*)", content)
    industry_match = re.search(r"\*\*產業:\*\* (.*)", content)
    mkt_cap_match = re.search(r"\*\*市值:\*\* (.*)", content)
    
    title_match = re.search(r"^# \d+ - (?:\[\[)?(.*?)(?:\]\])?$", content, re.M)
    ticker_match = re.search(r"^# (\d+)", content, re.M)
    
    # Extract sections
    biz_desc = ""
    supply_chain = ""
    
    sections = re.split(r"^## ", content, flags=re.M)
    for section in sections:
        if section.startswith("業務簡介"):
            biz_desc = section.replace("業務簡介\n", "").strip()
        elif section.startswith("供應鏈位置"):
            supply_chain = section.replace("供應鏈位置\n", "").strip()
            
    return {
        "ticker": ticker_match.group(1) if ticker_match else "Unknown",
        "company": title_match.group(1) if title_match else "Unknown",
        "sector": sector_match.group(1) if sector_match else "Unknown",
        "industry": industry_match.group(1) if industry_match else "Unknown",
        "biz_desc": biz_desc,
        "supply_chain": supply_chain,
        "raw_content": content
    }

if __name__ == "__main__":
    report_file = get_random_report()
    if report_file:
        data = parse_report(report_file)
        print(f"Selected: {data['company']} ({data['ticker']}) from {data['industry']}")
        # The agent will now take this data and use ollama_chinese to generate the post.
    else:
        print("No reports found.")
