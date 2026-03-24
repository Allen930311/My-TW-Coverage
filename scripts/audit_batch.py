import os
import re
import sys

# Configuration — paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_FILE = os.path.join(PROJECT_ROOT, "task.md")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "Pilot_Reports")

# --- Quality Rules (aligned with CLAUDE.md Golden Rules) ---

# Minimum proper-noun wikilinks per file (Golden Rule #3)
MIN_WIKILINKS = 8

# Words that indicate a generic/category wikilink (Golden Rule #1)
# These should appear as plain-text context, NOT inside [[ ]]
GENERIC_WIKILINK_MARKERS = [
    "大廠", "供應商", "客戶", "廠商", "原廠", "經銷商",
    "製造商", "業者", "企業", "公司", "代理商", "品牌商",
    "營運商", "貿易商", "通路商", "零售商", "承包商",
    "開發商", "服務商", "整合商",
]

# Banned placeholder strings (Golden Rule #6)
PLACEHOLDER_STRINGS = [
    "待 AI 補充",
    "待 [[AI]] 補充",
    "(待更新)",
    "基於嚴格實名制",
]

# Required metadata fields (Golden Rule #7)
REQUIRED_METADATA = ["板塊:", "產業:", "市值:", "企業價值:"]

# Required section headers
REQUIRED_SECTIONS = ["## 業務簡介", "## 供應鏈位置", "## 主要客戶及供應商", "## 財務概況"]

# English indicators for untranslated content (Golden Rule #5)
ENGLISH_INDICATORS = [
    "Business Description", "Inc.", "Ltd.", "manufactures",
    "provides", "is a company", "headquartered", "was founded",
    "specializes in", "engages in", "operates through",
]


def get_tickers_for_batch(batch_num):
    """Parses task.md to find tickers for a specific batch."""
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = re.compile(
            r"Batch\s+" + str(batch_num) + r"\*\*.*?:[:\s]*(.*)$",
            re.IGNORECASE | re.MULTILINE,
        )
        match = pattern.search(content)

        if match:
            ticker_str = match.group(1).strip()
            if ticker_str.endswith("."):
                ticker_str = ticker_str[:-1]

            raw_tickers = [t.strip() for t in ticker_str.split(",")]
            tickers = []
            for t in raw_tickers:
                m = re.search(r"(\d{4})", t)
                if m:
                    tickers.append(m.group(1))
            return tickers
        else:
            print(f"Error: Batch {batch_num} not found in {TASK_FILE}")
            return []

    except Exception as e:
        print(f"Error reading task.md: {e}")
        return []


def extract_wikilinks(content):
    """Return list of all [[wikilink]] strings in content."""
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def find_generic_wikilinks(wikilinks):
    """Return wikilinks that are generic category tags (violate Golden Rule #1)."""
    generic = []
    for wl in wikilinks:
        for marker in GENERIC_WIKILINK_MARKERS:
            if marker in wl:
                generic.append(wl)
                break
    return generic


def check_metadata(content):
    """Check that all required metadata fields exist and are not placeholder values."""
    issues = []
    for field in REQUIRED_METADATA:
        if field not in content:
            issues.append(f"Missing metadata: {field}")
        else:
            # Check for placeholder values in that field's line
            for line in content.split("\n"):
                if field in line:
                    if "(待更新)" in line or "N/A" not in line and line.strip().endswith(field):
                        # Field exists but might be empty — check there's content after the field
                        after_field = line.split(field, 1)[1].strip()
                        if not after_field:
                            issues.append(f"Empty metadata: {field}")
                    break
    return issues


def check_sections(content):
    """Check that all required sections exist."""
    missing = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)
    return missing


def check_section_depth(content):
    """Check that supply chain and customer sections have meaningful content (not single-line stubs)."""
    issues = []

    # Check supply chain section
    sc_match = re.search(
        r"## 供應鏈位置\n(.*?)(?=\n## 主要客戶及供應商|\Z)", content, re.DOTALL
    )
    if sc_match:
        sc_body = sc_match.group(1).strip()
        sc_lines = [l for l in sc_body.split("\n") if l.strip()]
        if len(sc_lines) < 3:
            issues.append(f"Supply chain too thin ({len(sc_lines)} lines)")

    # Check customers/suppliers section
    cs_match = re.search(
        r"## 主要客戶及供應商\n(.*?)(?=\n## 財務概況|\Z)", content, re.DOTALL
    )
    if cs_match:
        cs_body = cs_match.group(1).strip()
        cs_lines = [l for l in cs_body.split("\n") if l.strip()]
        if len(cs_lines) < 4:
            issues.append(f"Customers/suppliers too thin ({len(cs_lines)} lines)")

    return issues


def check_english(content):
    """Check first 20 lines for English indicators (skip metadata lines)."""
    intro_lines = content.split("\n")[:20]
    for line in intro_lines:
        if "**" in line or ":" in line:
            continue
        for indicator in ENGLISH_INDICATORS:
            if indicator in line:
                return indicator
    return None


def audit_ticker(content, verbose=False):
    """
    Run all quality checks on a single file's content.
    Returns (is_clean, issues_list).
    """
    issues = []

    # Check 1: Content length
    if len(content) < 200:
        issues.append("Content too short (<200 chars)")
        return False, issues  # No point checking further

    # Check 2: Placeholders (Golden Rule #6)
    for ph in PLACEHOLDER_STRINGS:
        if ph in content:
            issues.append(f"Placeholder found: '{ph}'")

    # Check 3: English content (Golden Rule #5)
    eng = check_english(content)
    if eng:
        issues.append(f"English text detected: '{eng}'")

    # Check 4: Required sections
    missing_sections = check_sections(content)
    for ms in missing_sections:
        issues.append(f"Missing section: {ms}")

    # Check 5: Metadata completeness (Golden Rule #7)
    meta_issues = check_metadata(content)
    issues.extend(meta_issues)

    # Check 6: Wikilink count (Golden Rule #3)
    wikilinks = extract_wikilinks(content)
    if len(wikilinks) < MIN_WIKILINKS:
        issues.append(f"Only {len(wikilinks)} wikilinks (minimum {MIN_WIKILINKS})")

    # Check 7: Generic wikilinks (Golden Rule #1 — MOST IMPORTANT)
    generic = find_generic_wikilinks(wikilinks)
    if generic:
        issues.append(f"Generic wikilinks ({len(generic)}): {generic}")

    # Check 8: Section depth — thin sections indicate low-effort enrichment
    depth_issues = check_section_depth(content)
    issues.extend(depth_issues)

    is_clean = len(issues) == 0
    return is_clean, issues


def audit_batch(batch_num, verbose=False):
    tickers = get_tickers_for_batch(batch_num)
    if not tickers:
        return

    print(f"QUALITY AUDIT: Checking {len(tickers)} tickers in Batch {batch_num}...")
    print(f"Rules: min {MIN_WIKILINKS} wikilinks, no generics, no placeholders, no English")
    print("=" * 60)

    clean_files = []
    needs_enrichment = []
    needs_quality_fix = []
    missing_files = []

    # Walk through all files in Pilot_Reports to find matches
    found_files = {}
    for root, dirs, files in os.walk(REPORTS_DIR):
        for file in files:
            if file.endswith(".md"):
                match = re.match(r"^(\d{4})", file)
                if match:
                    ticker = match.group(1)
                    if ticker in tickers:
                        found_files[ticker] = os.path.join(root, file)

    # Check each ticker
    for ticker in tickers:
        if ticker not in found_files:
            missing_files.append(ticker)
            continue

        file_path = found_files[ticker]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            is_clean, issues = audit_ticker(content, verbose)

            if is_clean:
                clean_files.append(ticker)
                if verbose:
                    wikilinks = extract_wikilinks(content)
                    print(f"  {ticker}: CLEAN ({len(wikilinks)} wikilinks)")
            else:
                # Categorize: "needs enrichment" (not started) vs "needs quality fix" (enriched but has issues)
                has_placeholder = any("待 AI 補充" in content or "待 [[AI]] 補充" in content
                                      for _ in [1])
                has_english = check_english(content) is not None
                is_too_short = len(content) < 200

                if has_placeholder or has_english or is_too_short:
                    needs_enrichment.append(ticker)
                    category = "NEEDS ENRICHMENT"
                else:
                    needs_quality_fix.append(ticker)
                    category = "NEEDS QUALITY FIX"

                if verbose:
                    print(f"  {ticker}: {category}")
                    for issue in issues:
                        print(f"    - {issue}")

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            needs_enrichment.append(ticker)

    # Summary
    print("=" * 60)
    print(f"CLEAN ({len(clean_files)}): {clean_files}")
    print(f"NEEDS ENRICHMENT ({len(needs_enrichment)}): {needs_enrichment}")
    if needs_quality_fix:
        print(f"NEEDS QUALITY FIX ({len(needs_quality_fix)}): {needs_quality_fix}")
    print(f"MISSING ({len(missing_files)}): {missing_files}")

    total = len(tickers)
    clean_pct = len(clean_files) / total * 100 if total > 0 else 0
    print(f"\nScore: {len(clean_files)}/{total} ({clean_pct:.0f}%) pass quality audit")


def audit_all_completed(verbose=False):
    """Audit all batches marked [x] in task.md to find quality regressions."""
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading task.md: {e}")
        return

    # Find all completed batch numbers
    completed = re.findall(r"\[x\]\s*\*\*Batch\s+(\d+)\*\*", content)
    if not completed:
        print("No completed batches found in task.md")
        return

    print(f"Auditing {len(completed)} completed batches: {', '.join(completed)}")
    print("=" * 60)

    total_clean = 0
    total_tickers = 0
    all_quality_issues = []

    for batch_num in completed:
        tickers = get_tickers_for_batch(batch_num)
        if not tickers:
            continue

        # Walk to find files
        found_files = {}
        for root, dirs, files in os.walk(REPORTS_DIR):
            for file in files:
                if file.endswith(".md"):
                    match = re.match(r"^(\d{4})", file)
                    if match:
                        ticker = match.group(1)
                        if ticker in tickers:
                            found_files[ticker] = os.path.join(root, file)

        batch_issues = []
        for ticker in tickers:
            if ticker not in found_files:
                continue
            try:
                with open(found_files[ticker], "r", encoding="utf-8") as f:
                    file_content = f.read()
                is_clean, issues = audit_ticker(file_content)
                total_tickers += 1
                if is_clean:
                    total_clean += 1
                else:
                    batch_issues.append((ticker, issues))
            except Exception:
                pass

        if batch_issues:
            print(f"\nBatch {batch_num}: {len(batch_issues)} tickers need quality fixes")
            if verbose:
                for ticker, issues in batch_issues:
                    print(f"  {ticker}:")
                    for issue in issues:
                        print(f"    - {issue}")
            all_quality_issues.extend(batch_issues)

    print("\n" + "=" * 60)
    clean_pct = total_clean / total_tickers * 100 if total_tickers > 0 else 0
    print(f"OVERALL: {total_clean}/{total_tickers} ({clean_pct:.0f}%) pass quality audit")
    print(f"Total tickers needing quality fix: {len(all_quality_issues)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python audit_batch.py <batch_number> [-v]     Audit a single batch")
        print("  python audit_batch.py --all [-v]              Audit all completed batches")
        sys.exit(1)

    verbose = "-v" in sys.argv

    if sys.argv[1] == "--all":
        audit_all_completed(verbose)
    else:
        batch_num = sys.argv[1]
        audit_batch(batch_num, verbose)
