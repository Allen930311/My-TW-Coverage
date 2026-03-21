import os
import glob

tickers = ['1319', '1336', '1338', '1339', '1506', '1512', '1521', '1522', '1524', '1525', '1533', '1536', '1563', '1568', '1587']
output = []
for t in tickers:
    matches = glob.glob(f'F:/My TW Coverage/Pilot_Reports/Auto Parts/{t}_*.md')
    if matches:
        with open(matches[0], 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines()[:10]]
            output.append(f'--- {os.path.basename(matches[0])} ---\n' + '\n'.join(lines))
    else:
        output.append(f'{t} NOT FOUND')
print('\n\n'.join(output))
