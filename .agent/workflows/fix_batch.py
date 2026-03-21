import os
import glob
import sys
import re

# Add current dir to path to import data chunks
sys.path.append(os.path.dirname(__file__))

DATA = {
    "4546": {
        "desc": "長亨精密 (4546) 是一家專注於[[航空發動機]]關鍵零組件研發與製造的高階精密金屬加工廠。公司主力產品為飛機引擎葉片及各類組合件，是全球少數能直供前三大航空引擎製造商的 Tier 1 供應商。憑藉先進製程技術，公司多項引擎零組件產品擁有全球市占第一的地位，產品 100% 外銷歐美大廠。",
        "up": "[[航太級金屬材料商]] (供應鈦合金、特殊鋼等).",
        "mid": "**長亨** (飛機引擎葉片及高階精密零組件製造).",
        "down": "[[航空發動機原廠]] (OEMs).",
        "cust": "[[賽峰集團]] (Safran/Snecma), [[奇異]] (GE), [[勞斯萊斯]] (Rolls-Royce), [[普惠]] (Pratt & Whitney).",
        "supp": "[[國際航太材料供應商]]."
    },
    "1712": {
        "desc": "興農 (1712) 是一家多元化經營的台灣企業集團，本業為[[植物保護劑]] (農藥) 與特用化學品製造，同時跨足連鎖超市 ([[楓康超市]])、家用品與[[團膳]] (玉美生技)、以及預拌混凝土。其中，植物保護業務外銷遍及全球近百國，超市與團膳事業則在中台灣擁有穩固的區域優勢與民生內需客群。",
        "up": "[[跨國農藥大廠]] (授權或供應原體), [[化工原料大廠]].",
        "mid": "**興農** (農藥合成代工/配方、超市通路零售、生鮮團膳).",
        "down": "[[各國農民]]與[[農業經銷體系]], [[一般消費者]], [[企業團膳客戶]].",
        "cust": "[[台灣農民]], 個體[[消費者]] (楓康超市), [[海外農業經銷商]], [[大型賣場]].",
        "supp": "[[國際農化原料廠]]."
    },
    "1722": {
        "desc": "台灣肥料 (1722) 是台灣市佔率最高的[[肥料]]與化工產品製造商，且擁有龐大土地資產，積極進行[[不動產開發]]與收租 (如南港商辦案)。近年來，公司配合減碳趨勢，轉型投入[[潔淨能源]]領域，引進並開發[[電子級藍氨]]，積極爭取打入台灣高階[[半導體供應鏈]]。",
        "up": "[[國外原物料供應商]] (進口液氨、尿素、氯化鉀等), [[朱拜爾肥料公司]].",
        "mid": "**台肥** (肥料與尿素化工品生產、商用不動產開發、藍氨供應).",
        "down": "[[台灣農民]] (肥料), [[化工廠]] (工業級硝酸), [[半導體製造商]] (電子級藍氨).",
        "cust": "[[農業從業人員]], [[台積電]] (潛在藍氨客戶), [[商辦及旅館租戶]].",
        "supp": "[[沙烏地阿拉伯基本工業公司]] (SABIC), [[國際化肥原料商]]."
    },
    "6508": {
        "desc": "惠光 (6508) 是一家主要從事[[植物保護劑]] (農藥) 及[[地工合成材料]]製造的化學公司。在農業科技方面，公司代理並配製農藥販售於國內外市場；在環境科技方面，其地工防滲膜等產品廣泛應用於掩埋場、礦業、蓄水池等工程，積極拓展海外礦業專案客戶，是台灣地工膜領導廠商。",
        "up": "[[國際農藥原廠]] (供應農藥原體), [[石化大廠]] (供應塑膠粒等防滲膜原料).",
        "mid": "**惠光** (農藥配方加工製造、地工防滲膜製造).",
        "down": "[[農藥代銷商]]與[[農民]], [[環保工程公司]], [[海外礦業開發商]].",
        "cust": "[[日本國際農藥大廠]] (OEM代工), [[中國大陸代理商]], 各國[[礦業公司]] (地工膜).",
        "supp": "[[跨國農化公司]], [[大型石化廠]]."
    }
}

BASE_DIR = r"F:\My TW Coverage\Pilot_Reports"

def update_file(filepath, ticker):
    if ticker not in DATA:
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_data = DATA[ticker]
    
    # 1. Business Description (Handle optional metadata)
    # We replace everything between the end of metadata (or ## 業務簡介) and ## 供應鏈位置
    # We look for "企業價值: ... \n\n" or just "## 業務簡介\n"
    def repl_desc(m):
        header_part = m.group(1)
        return f"{header_part}{new_data['desc']}\n"
        
    content = re.sub(
        r'(## 業務簡介\n(?:.*?企業價值:.*?\n\n|))(.*?)(?=\n## 供應鏈位置)', 
        repl_desc, 
        content, 
        flags=re.DOTALL
    )
    
    # 2. Supply Chain Data
    supply_chain_text = f"*   **上游**: {new_data['up']}\n" \
                        f"*   **中游**: {new_data['mid']}\n" \
                        f"*   **下游**: {new_data['down']}\n"
    content = re.sub(
        r'(## 供應鏈位置\n)(.*?)(?=\n## 主要客戶及供應商)',
        rf'\g<1>{supply_chain_text}', 
        content, 
        flags=re.DOTALL
    )
    
    # 3. Key Customers & Suppliers
    cust_supp_text = f"### 主要客戶\n*   {new_data['cust']}\n\n" \
                     f"### 主要供應商\n*   {new_data['supp']}\n"
    content = re.sub(
        r'(## 主要客戶及供應商\n)(.*?)(?=\n## 財務概況)',
        rf'\g<1>{cust_supp_text}', 
        content, 
        flags=re.DOTALL
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Enriched: {os.path.basename(filepath)}")

def main():
    for filepath in glob.glob(os.path.join(BASE_DIR, "**", "*.md"), recursive=True):
        filename = os.path.basename(filepath)
        match = re.search(r'^(\d{4})_', filename)
        if match:
            ticker = match.group(1)
            if ticker in DATA:
                update_file(filepath, ticker)

if __name__ == "__main__":
    main()
