import os
import glob
import re

FILES_TO_SCRUB = {
    r"F:\My TW Coverage\Pilot_Reports\Advertising Agencies\6136_富爾特.md": {
        "up": "[[瑞昱]]",
        "down": "[[中華電信]], [[萬里雲]], [[曙客]], [[大聯大控股]]",
        "cust": "[[中華電信]], [[萬里雲]], [[曙客]], [[大聯大控股]]",
        "supp": "[[中華電信]], [[瑞昱]]"
    },
    r"F:\My TW Coverage\Pilot_Reports\Agricultural Inputs\1712_興農.md": {
        "up": "[[先正達]]",
        "down": "[[楓康超市]], [[玉美生技]]",
        "cust": "[[楓康超市]], [[玉美生技]]",
        "supp": "[[先正達]]"
    },
    r"F:\My TW Coverage\Pilot_Reports\Agricultural Inputs\1722_台肥.md": {
        "up": "[[沙烏地阿拉伯基本工業公司]], [[朱拜爾肥料公司]]",
        "down": "[[台積電]]",
        "cust": "[[台積電]]",
        "supp": "[[沙烏地阿拉伯基本工業公司]], [[朱拜爾肥料公司]]"
    },
    r"F:\My TW Coverage\Pilot_Reports\Agricultural Inputs\6508_惠光.md": {
        "up": "[[先正達]], [[巴斯夫]]",
        "down": "[[日本住友化學]]",
        "cust": "[[日本住友化學]]",
        "supp": "[[先正達]], [[巴斯夫]]"
    }
}

for filepath, changes in FILES_TO_SCRUB.items():
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex replacements to precisely target the lines
    content = re.sub(r'^\*\*上游 \(原料/設備\):\*\*\n.*$', f"**上游 (原料/設備):**\n- {changes['up']}", content, flags=re.MULTILINE)
    content = re.sub(r'^\*\*下游應用:\*\*\n.*$', f"**下游應用:**\n- {changes['down']}", content, flags=re.MULTILINE)
    content = re.sub(r'^### 主要客戶\n.*$', f"### 主要客戶\n- {changes['cust']}", content, flags=re.MULTILINE)
    content = re.sub(r'^### 主要供應商\n.*$', f"### 主要供應商\n- {changes['supp']}", content, flags=re.MULTILINE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Scrubbed and updated {filepath}")
