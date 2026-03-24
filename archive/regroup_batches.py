import os
import re

base_dir = r"f:\My TW Coverage\Pilot_Reports"
task_file = r"f:\My TW Coverage\task.md"

folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
folders.sort()

batches = []

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    
    tickers = []
    for f in files:
        # Match starting digits
        match = re.search(r'^(\d+)', f)
        if match:
            tickers.append((int(match.group(1)), match.group(1))) # store both int for sorting and string for output
            
    # Sort numerically
    tickers.sort(key=lambda x: x[0])
    
    # Extract string representations
    ticker_strs = [t[1] for t in tickers]
    
    # Chunk by max 30
    chunk_size = 30
    for i in range(0, len(ticker_strs), chunk_size):
        chunk = ticker_strs[i:i + chunk_size]
        batches.append((folder, chunk))

# Build new batch strings
new_batch_lines = []
for idx, (folder, chunk) in enumerate(batches, 1):
    tick_str = ", ".join(chunk)
    # The user example: "First 30 tickers in Advertising Agencies will be the first batch."
    # Adding the folder name for clarity is a good idea.
    new_batch_lines.append(f"        - [ ] **Batch {idx}** ({folder}): {tick_str}")

new_batches_text = "\n".join(new_batch_lines)

# Read task.md
with open(task_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the old batches block
# We find the Enrichment phase start and Verification phase start
start_marker = "    - [/] **Batch Enrichment**: Systematically enrich reports with AI research (Intro + Supply Chain) <!-- id: 15 -->\n"
end_marker = "\n- [/] Verification Phase <!-- id: 16 -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    start_point = start_idx + len(start_marker)
    # Replace the middle part
    new_content = content[:start_point] + new_batches_text + content[end_idx:]
    with open(task_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Successfully replaced. Total new batches: {len(batches)}")
else:
    print("Could not find markers in task.md")
