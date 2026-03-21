---
description: Workflow to enrich a single company ticker file with AI-generated, company-specific content.
---

# Enrich Ticker Workflow

This workflow is used to enrich a company's Markdown report with business details, supply chain position, and key customers/suppliers using AI.

## Prerequisites
- The target Markdown file must already exist (e.g., `f:\My TW Coverage\Pilot_Reports\Industry\Ticker_Name.md`).
- Only run this workflow when you are viewing the specific file you want to enrich.

## CRITICAL RULES
- **UTF-8 Encoding**: Every file write or modification MUST use UTF-8 encoding. Never use default shell encoding (like `Set-Content` without `-Encoding utf8`).
- **Clean Filenames**: NEVER use URL-encoded characters in filenames (e.g., use `3624_光頡.md`, NOT `3624_%E5%85%89%E9%A0%A1.md`).
- **Clean Overwrite**: If a file is suspected of containing binary junk or encoding errors, delete it via terminal before writing the fresh content.
- **Data Integrity**: **Metadata** (`板塊`, `產業`, `市值`, `企業價值`) and **Financial Tables** MUST be preserved exactly as they are in the original file. 
    - **CRITICAL FAIL-SAFE**: If the metadata block (`**板塊:**...`) is completely missing, or if any field contains `(待更新)` or `*(待 AI 補充)*`, you MUST find the exact information via deep web search (or `yfinance`) and explicitly INJECT IT. **NEVER** leave `(待更新)` placeholders for Market Cap or Enterprise Value. Convert billions (億) to millions (百萬) where necessary. If Enterprise Value is fundamentally unavailable (e.g., for Banks), explicitly write `N/A 百萬台幣`.
    - **CRITICAL FAIL-SAFE**: If the `## 主要客戶及供應商` header is completely missing from the base file, you MUST explicitly insert the header and its content right above `## 財務概況`.
- **No Python Injection Scripts (`temp.py`)**: Do NOT write batch Python scripts to perform regex replacements on the Markdown files. Use your native `write_to_file` or `multi_replace_file_content` tools to edit files directly. Python scripts are brittle, fail silently on missing headers, and clutter the workspace.
- **No Lazy Omissions & Specificity Mandate**: The phrase `(基於嚴格實名制，因未查獲確切客戶全名而予省略)` and placeholders like `*(待 AI 補充)*` are STRICTLY BANNED. You MUST perform extreme deep web searches to find **specific entity names** (the more specific the better). Only fall back to descriptive generics (e.g., `[[北美大型汽車零配件連鎖巨頭]]`) if specific names are genuinely hidden behind NDAs after exhaustive search. 
- **Universal Tagging Rule (Gold Standard)**: EVERY identifiable entity and key product/technology MUST be wrapped in `[[Wikilinks]]`. **Every file MUST contain a minimum of 8 concise, noun-based wikilinks.** Do not use bolding inside the wikilinks. Consistency is mandatory (tag `[[Broadcom]]` and `[[Jabil]]`).

## Steps

0.  **Missing File Procedure (If file does not exist)**:
    - If the target file is missing, you must generate it first.
    - Run the following command in the terminal:
      ```powershell
      # Optional: Providing --name helps create the correct filename immediately
      python "f:\My TW Coverage\02_generate_base_reports.py" --ticker <TICKER> --name "<COMPANY_NAME>"
      ```
    - **Note**: The script will check `Taiwan Stock Exception.xlsx`. If the ticker is in the exception list, it will skip generation.
    - Check the output to see where the file was created (usually in `f:\My TW Coverage\Pilot_Reports`).
    - Once generated (or skipped), proceed to **Step 1**.

1.  **Read the Target File**:
    - Use `view_file` to read the content of the Markdown file for the specific ticker.
    - **CRITICAL:** Note the existing metadata/header lines at the top of the file, specifically:
        - `板塊:` (Sector)
        - `產業:` (Industry)
        - `市值:` (Market Cap)
        - `企業價值:` (Enterprise Value)
    - **YOU MUST PRESERVE THESE LINES EXACTLY AS THEY ARE.** Do not overwrite, translate, or delete them.

2.  **Research the Company**:
    - Use `search_web` to find information about the company (Ticker + Name).
    - **NO LAZY RESEARCH**: You MUST dig deep to find EXACT company names. Query specifically for `[Ticker] 法說會`, `[Ticker] 年報`, or `[Ticker] 主要供應商/客戶`.
    - **ANTI-LAZINESS MANDATE**: The quality and integrity of your research MUST NOT degrade as you progress through multiple batches. Treat the 50th ticker with the exact same rigorous deep-search standard as the 1st ticker. NEVER resort to guessing or generic filling just to save time.
    - Focus on finding:
        - **Business Description**: What does the company do? What are its main products/services? History?
        - **Supply Chain Position**: Where does it sit in the supply chain (Upstream, Midstream, Downstream)? Who are its upstream suppliers and downstream customers? (Generic categories are allowed here).
        - **Key Customers & Suppliers**: Specific names of major customers and suppliers. If exact names are hidden, find their closest identifiable partners or competitors.

3.  **Enrich the Report (Write to File)**:
    - Use `write_to_file` to overwrite the *entire* file with the enriched content.
    - **Structure:**
        - **Header**: Keep the `# Ticker - Name` header.
        - **Metadata**: **RESTORE the `板塊`, `產業`, `市值`, `企業價值` lines exactly as they were in the original file.** If they were missing, manually insert them based on your research in the exact format shown in the Example Output.
        - **Business Description (業務簡介)**:
            - **REPLACE the entire original English description** with a **Traditional Chinese** translation.
            - **COMPREHENSIVE TAGGING:** Add `[[Wikilinks]]` for every major product, manufacturing process, and target market. This data is used to find "product peers" and competitors.
            - **ENSURE the original English text is completely removed.**
            - Ensure the tone is professional and informative.
        - **Supply Chain Position (供應鏈位置)**:
            - **ENHANCED FORMATTING MANDATE (Segmented Detail)**: You MUST format this section extensively using detailed, segmented categories rather than forcing all data into 3 single lines. 
            - Group the supply chain by Business Segment, Process, or Category. Use bold headers for the upstream/midstream/downstream phase, followed by bulleted sub-categories.
              Example:
              **上游 (原料與能源):**
              - **核心原料:** [[石灰石]], 砂石...
              - **能源:** [[太陽能]], 風電...
              **下游應用 (終端市場):**
              - **基礎建設:** 機場, 港口...
              - **科技廠房:** 半導體廠...
            - It is highly encouraged to use specific industry categories or asset types here if exact names belong in the next section.
        - **Key Customers & Suppliers (主要客戶及供應商)**:
            - **ENHANCED FORMATTING MANDATE**: Break down the specific clients and suppliers by Business Segment, Industry, or Product Category using bullet points. Do not lump them together.
            - **STRICT MANDATE (SPECIFIC COMPANY NAMES)**: You MUST ALWAYS strive for specific, exact company names (e.g., `[[Apple]]`, `[[Tesla]]`, `[[台積電]]`, `[[聯發科]]`) inside these segments. 
            - **Web Search Deep-Dive**: You must exhaustively search the web (including annual reports and investor conferences) to find real corporate entity names. 
            - **DO NOT** use placeholders like `[[一般消費者]]` or `[[國際大廠]]`. Generic descriptions are only allowed as an absolute last resort.
        - **Financial Overview (財務概況)**:
            - **KEEP THE FINANCIAL SECTION UNTOUCHED.**
            - If the original file had a financial table or placeholder, preserve it exactly. Do not regenerate or modify the financial data unless explicitly instructed.

## Example Output Format (Enhanced Gold Standard)

```markdown
# 1234 - Example Co

## 業務簡介
**板塊:** Technology
**產業:** Electronic Components
**市值:** 10,000 百萬台幣
**企業價值:** 12,000 百萬台幣

Example Co 是一家專注於 [[半導體]] 封測的廠商... (Traditional Chinese description with [[wikilinks]])

## 供應鏈位置
**上游 (原料設備):**
- **晶圓製造:** 採購自 [[TSMC]], [[聯電]].
- **封裝材料:** 採購 [[導線架]], [[封裝膠]].

**下游應用 (終端市場):**
- **消費性電子:** 智慧型手機, 平板電腦.
- **車用市場:** 供應給 [[電動車]] 製造商.

## 主要客戶及供應商
### 主要客戶
- **智慧手機:** [[Apple]], [[Samsung]].
- **AI 伺服器:** [[NVIDIA]], [[Supermicro]].

### 主要供應商
- **晶圓製造:** [[TSMC]], [[GlobalFoundries]].
- **封裝設備:** [[KLA]], [[ASML]].

## 財務概況 (單位: 百萬台幣, 只有 Margin 為 %)
(Preserve existing financial tables)
...
```

4.  **Verification**:
    - Review the generated file to ensure:
        - Metadata lines are present and correct.
        - Business description is in Traditional Chinese with a minimum of 8 strict `[[wikilinks]]`.
        - **NO original English description remains.**
        - **NO placeholders like `*(待 AI 補充)*` or robotic omission phrases remain.** Re-research if found.
        - Financial section is present and unmodified.
