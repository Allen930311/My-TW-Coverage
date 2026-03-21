import os
import re
import sys

# Configuration
TASK_FILE = r"f:\My TW Coverage\task.md"
REPORTS_DIR = r"f:\My TW Coverage\Pilot_Reports"

def get_tickers_for_batch(batch_num):
    """Parses task.md to find tickers for a specific batch."""
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex to find the batch line: e.g., "- [ ] **Batch 1** (Advertising Agencies): 6136"
        pattern = re.compile(r"Batch\s+" + str(batch_num) + r"\*\*.*?:[:\s]*(.*)$", re.IGNORECASE | re.MULTILINE)
        match = pattern.search(content)
        
        if match:
            # Extract the part after the colon
            ticker_str = match.group(1).strip()
            # Remove any trailing comments or markdown artifacts if necessary (though usually clean)
            # Remove period at end if exists
            if ticker_str.endswith('.'):
                ticker_str = ticker_str[:-1]
                
            # Split by commas and clean up
            # Also handle modifiers like (x) or (c) attached to the tickers in the list
            raw_tickers = [t.strip() for t in ticker_str.split(',')]
            tickers = []
            for t in raw_tickers:
                # Extract just the first 4 consecutive digits
                m = re.search(r'(\d{4})', t)
                if m:
                    tickers.append(m.group(1))
            return tickers
        else:
            print(f"Error: Batch {batch_num} not found in {TASK_FILE}")
            return []
            
    except Exception as e:
        print(f"Error reading task.md: {e}")
        return []

def audit_batch(batch_num):
    tickers = get_tickers_for_batch(batch_num)
    if not tickers:
        return

    print(f"STRICT AUDIT: Checking {len(tickers)} tickers in Batch {batch_num}...")
    
    clean_files = []
    needs_enrichment = []
    missing_files = []

    # Walk through all files in Pilot_Reports to find matches
    found_files = {}
    for root, dirs, files in os.walk(REPORTS_DIR):
        for file in files:
            if file.endswith(".md"):
                # Extract ticker from filename (assuming "XXXX_Name.md" or just "XXXX.md")
                match = re.match(r"^(\d{4})", file)
                if match:
                    ticker = match.group(1)
                    if ticker in tickers:
                        found_files[ticker] = os.path.join(root, file)

    # Check each ticker
    for ticker in tickers:
        if ticker not in found_files:
            missing_files.append(ticker)
            # print(f"Ticker {ticker}: MISSING FILE") # Optional: reduce noise if expected
            continue

        file_path = found_files[ticker]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Strict Check 1: Content must not be empty or too short
            if len(content) < 200:
                needs_enrichment.append(ticker)
                print(f"Ticker {ticker}: Content too short (<200 chars)")
                continue

            # Strict Check 2: Must NOT contain placeholder
            if "待 AI 補充" in content or "待 [[AI]] 補充" in content:
                needs_enrichment.append(ticker)
                print(f"Ticker {ticker}: Found placeholder (待 AI 補充)")
                continue
            
            # Strict Check 3: Check for English Introduction (Simple heuristic)
            # We look at the first few lines for English-only indicators
            intro_lines = content.split('\n')[:20]
            english_indicators = ["Business Description", "Inc.", "Ltd.", "manufactures", "provides", "is a company"]
            is_english = False
            for line in intro_lines:
                # Skip metadata lines
                if "**" in line or ":" in line: continue
                for indicator in english_indicators:
                    if indicator in line:
                        is_english = True
                        break
                if is_english: break
            
            if is_english:
                needs_enrichment.append(ticker)
                print(f"Ticker {ticker}: Found English indicator (Needs Translation)")
                continue

            clean_files.append(ticker)
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            needs_enrichment.append(ticker)

    print("-" * 30)
    print(f"CLEAN ({len(clean_files)}): {clean_files}")
    print(f"NEEDS ENRICHMENT ({len(needs_enrichment)}): {needs_enrichment}")
    print(f"MISSING ({len(missing_files)}): {missing_files}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit_batch.py <batch_number>")
    else:
        batch_num = sys.argv[1]
        audit_batch(batch_num)
