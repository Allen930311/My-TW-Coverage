# Master Workflow Documentation: Efficient Batch Enrichment

## Core Philosophy: "Efficiency through Batching & Automation"
This project prioritizes high-throughput enrichment without constant user interruptions. We achieve this by using automated auditing tools and processing entire batch groups in single, coordinated runs.

---

## 1. Batch Identification & Initial Audit
Instead of searching for files manually, start by identifying the target batch from `task.md`.

1.  **Run Audit**: Run the strict audit script with the verbose flag to identify exactly which tickers need work.
    ```powershell
    python "f:\My TW Coverage\.agent\workflows\audit_batch.py" <batch_num> -v
    ```
2.  **Verify Filenames**: If the audit says a ticker exists but you suspect a name mismatch, verify the filename:
    ```powershell
    python .agent\workflows\find_by_name.py --pattern "<TICKER>_*.md"
    ```
3.  **Identify Targets**: Focus only on tickers listed under `NEEDS ENRICHMENT`.

---

## 2. The "Group of 10" Execution Loop
To maintain stability and progress tracking, process tickers in groups of **10** at a time.

### Phase A: Research (10 Tickers)
1.  **Research**: Use `search_web` for a group of 10 tickers sequentially.
2.  **Format**: Convert the research into a `DATA` dictionary compatible with `fix_batch.py`.
    -   **Business Intro**: Professional Traditional Chinese, removing all original English.
    -   **Comprehensive Tagging (Gold Standard)**: A minimum of 8 concise, noun-based, unbolded `[[Wikilinks]]` per file. Tag **every** key product and technology (e.g. `[[AI 伺服器]]`, `[[ABF 載板]]`). This is the foundation for finding competitors.
    -   **Supply Chain / Clients / Suppliers (ENHANCED GOLD STANDARD)**: You MUST break these sections down by **Business Segment/Category** using bullet points. Explicit Top/Mid/Downstream (`上游`/`中游`/`下游`) must still exist for the supply chain, but populated with categorized sub-bullets. Strive for specific, exact client and supplier company names (e.g., `[[Apple]]`, `[[日月光]]`, `[[Tesla]]`) within these segments. PLACEHOLDERS ARE BANNED.
    -   **Wikilinks**: Ensure all technical terms and partner companies are tagged.

### Phase B: Injection & Execution
1.  **Inject Payload**: Use `replace_file_content` to overwrite the `DATA` dictionary in `f:\My TW Coverage\.agent\workflows\fix_batch.py`.
2.  **Run Script**: Execute the update script:
    ```powershell
    python "f:\My TW Coverage\.agent\workflows\fix_batch.py"
    ```
3.  **Verify**: Re-run the audit flag (`-v`) for the batch to confirm the 10 tickers moved to `CLEAN`.

---

## 3. General Rules & Best Practices
- **UTF-8 ONLY**: Always use UTF-8 for reading and writing.
- **Data Integrity**: **NEVER** modify or regenerate the Financial Tables section.
- **Traditional Chinese**: All content (Desc, Supply Chain, Clients) must be in Traditional Chinese.
- **Agent Autonomy**: Once a group of 10 is verified clean, move immediately to the next 10 without prompting the user. Only ask for review after the *entire* batch of 30 is complete.
- **No Disposable Scripts**: Always use the `DATA` dict in `fix_batch.py`.

## 4. Anti-Variability & Execution Rigidity
To ensure 100% consistency across sessions and different agents:
- **NO NEW SCRIPTS**: The agent is strictly forbidden from creating temporary Python scripts (e.g., `temp_inject.py`). All data injection MUST happen via the `DATA` dictionary in the canonical `f:\My TW Coverage\.agent\workflows\fix_batch.py`.
- **FIXED COMMAND SET**: Execution must strictly follow the **7-Command Approval Pattern** (1 Audit + 3 loops of 2 commands). Any deviation or "creative" execution manner is a violation of this Skill.
- **TAGGING PARITY**: If a report mentions multiple entities (e.g. `[[Broadcom]]` and `Jabil`), the agent **MUST** tag both. Partial tagging is considered a failure of the Universal Tagging Rule.

---

## 5. Key Scripts & Tools
- `audit_batch.py`: Discovery and verification.
- `fix_batch.py`: The ONLY authorized script for file updates.
- `enrich-ticker.md`: Detailed report formatting rules.

---

## 6. Definition of "Batch Completed" (CRITICAL STRATEGY)
The user has strictly defined that marking a batch as "Completed" means **every single .md file** within the batch MUST securely possess:
1. **Intact Metadata**: The `板塊`, `產業`, `市值`, and `企業價值` lines MUST be present. If they were missing from base generation, the Agent MUST research and organically inject them. If the values contain `(待更新)`, the Agent MUST fetch the exact values (e.g., via web search for market cap) and replace the placeholders.
2. **Gold Standard Supply Chain**: Explicitly structured with `上游`/`中游`/`下游`.
3. **Major Customers & Suppliers**: Must consist of **EXACT COMPANY NAMES** (e.g., `[[Intel]]`, `[[Nvidia]]`, `[[鴻海]]`) rather than broad generic entity types, leaving zero placeholders.
4. **Translated Description**: Professional Traditional Chinese, completely devoid of the original English text.
5. **Intact Financials**: The formatted financial data tables MUST remain strictly preserved and not accidentally deleted.

## 7. Standard Operation for "Run Enrichment for Batch X"
When the user gives this command, the agent must:
1. Load this document to remember the strict completion criteria.
2. Run Step 1 (Audit) and perform a **Pre-Enrichment Verification** to check if files are natively missing the baseline metadata block or contain `(待更新)`.
3. Execute Phase A & B in loops of 10 until the batch is enriched.
4. Perform a **Post-Batch Review** ensuring zero `(待更新)` or `*(待 AI 補充)*` placeholders remain in any field (Metadata, Supply Chain, Clients/Suppliers).
5. Notify the user only when the batch is finished and 100% compliant, or a major blocker is found.
