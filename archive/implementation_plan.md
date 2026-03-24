# Implementation Plan - Batch-Agnostic Audit Script

## Goal
Create a generic `audit_batch.py` script that can audit *any* batch by reading the ticker list directly from `task.md`. This eliminates the need to create separate audit scripts for each batch.

## Proposed Changes
### [NEW] `f:\My TW Coverage\audit_batch.py`
- **Functionality**:
    - Accepts a batch number as a command-line argument (e.g., `python audit_batch.py 22`).
    - Parses `f:\My TW Coverage\task.md` to find the line corresponding to the specified batch.
    - Extracts the list of tickers from that line.
    - Performs the strict audit checks (file existence, content length > 200 chars, no `*(待 AI 補充)*` placeholders, no English-only introduction).
    - Outputs the list of Clean, Needs Enrichment, and Missing files.
- **Key Logic**:
    - **Regex for `task.md`**: `r"Batch\s+" + str(batch_num) + r"[\*\s]*:(.*)$"` (case insensitive).
    - **Audit Logic**: reused from `audit_batch_21_strict.py`.

## Verification Plan
### Automated Tests
- **Test 1: Verify Batch 21 (Known Good)**
    - Run: `python "f:\My TW Coverage\audit_batch.py" 21`
    - Expected Output: All 30 files CLEAN.
- **Test 2: Verify Batch 22 (New/Empty)**
    - Run: `python "f:\My TW Coverage\audit_batch.py" 22`
    - Expected Output: 30 files MISSING or NEEDS ENRICHMENT (mostly MISSING since they haven't been touched).

### Manual Verification
- None required beyond running the script.
