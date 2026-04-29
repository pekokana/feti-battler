import hashlib
import random
import argparse
import sys

def get_rarity(total_score):
    if total_score >= 8600:
        return "LEGEND", "amber-500", "amber-400" # 名前, 枠色, タイトル色
    elif total_score >= 7800:
        return "EPIC", "purple-500", "purple-300"
    elif total_score >= 6000:
        return "RARE", "blue-500", "blue-300"
    else:
        return "COMMON", "gray-500", "gray-100"

def get_material_name(seed):
    material_val = int(seed[10:13], 16) % 255
    prefixes = ["轟天の", "静寂の", "黄金の", "混沌の", "氷結の", "紅蓮の", "宵闇の", "閃光の", "比類なき", "覚醒せし"]
    p_name = prefixes[material_val % len(prefixes)]
    
    if material_val < 50: m = "黒鉄の焔"
    elif material_val < 110: m = "大地の息吹"
    elif material_val < 170: m = "深淵の水鏡"
    elif material_val < 230: m = "天上の福音"
    else: m = "虚無の残光"
    return f"{p_name}{m}"

def mine_units(target_sum, num_results, spd=None, df=None, luk=None, max_retry=1000000, output_lp=False):
    print(f"--- 探索設定 ---")
    print(f"  目標合計(HP+ATK): {target_sum}+")
    print(f"  最大試行回数: {max_retry}")
    print(f"----------------")

    found_count = 0
    tries = 0
    found_data_list = []

    current_val = random.randint(0, 10**9)

    while found_count < num_results and tries < max_retry:
        tries += 1
        seed = hashlib.sha256(str(current_val).encode()).hexdigest()[:20]
        
        hp = int(seed[0:4], 16) % 5000 + 3000
        atk = int(seed[4:8], 16) % 1000 + 500
        s = int(seed[8:12], 16) % 100 + 10
        d = int(seed[12:16], 16) % 300 + 100
        l = int(seed[16:20], 16) % 20 + 5
        
        total_score = hp + atk
        
        if total_score >= target_sum:
            match = True
            if spd is not None and abs(s - spd) > 5: match = False
            if df is not None and abs(d - df) > 20: match = False
            if luk is not None and abs(l - luk) > 2: match = False
            
            if match:
                found_count += 1
                rarity, border_col, title_col = get_rarity(total_score)
                name = get_material_name(seed)
                
                print(f"\n✨ [{found_count}] {rarity} 発見!")
                print(f"   Name: {name}")
                print(f"   Code: {seed} | SUM:{total_score} (HP:{hp} ATK:{atk})")
                
                found_data_list.append({
                    "seed": seed, "name": name, "hp": hp, "atk": atk, 
                    "sum": total_score, "rarity": rarity, 
                    "border_col": border_col, "title_col": title_col
                })
        
        current_val += 1
        if tries % 50000 == 0:
            print(f"\r探索中... {tries}/{max_retry} 試行完了", end="", flush=True)

    # --- LP用HTML出力 ---
    if output_lp and found_data_list:
        print("\n\n" + "="*70)
        print("  【LP掲載用ソース】以下の grid コンテナの中に貼り付けてください")
        print("  <div class=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8\">")
        print("="*70 + "\n")
        
        for data in found_data_list:
            html = f"""
            <div class="bg-gray-800 border-2 border-{data['border_col']} p-6 rounded-2xl relative overflow-hidden flex flex-col justify-between shadow-xl shadow-{data['border_col'].split('-')[0]}-900/10">
                <div>
                    <div class="absolute top-0 right-0 bg-{data['border_col']} text-black text-[10px] font-bold px-2 py-0.5">{data['rarity']}</div>
                    <h3 class="text-lg font-bold text-{data['title_col']} mb-2 text-left">{data['name']}</h3>
                    <div class="flex justify-between text-xs mb-4 text-gray-400 font-mono">
                        <span>HP: {data['hp']}</span>
                        <span>ATK: {data['atk']}</span>
                        <span class="text-{data['title_col']} font-bold">SUM: {data['sum']}</span>
                    </div>
                </div>
                
                <div>
                    <div class="bg-black/40 p-2.5 rounded font-mono text-[11px] flex justify-between items-center text-gray-300 border border-white/5">
                        <span class="truncate mr-2">{data['seed']}</span>
                        <button onclick="navigator.clipboard.writeText('{data['seed']}')" class="shrink-0 text-[10px] bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded transition-colors">COPY</button>
                    </div>
                    <p class="text-[10px] mt-3 text-gray-500 italic leading-tight text-left">
                        ※{data['rarity']}級の個体。バトルアプリにコードを貼り付けて召喚可能です。
                    </p>
                </div>
            </div>"""
            print(html)
        print("\n" + "="*70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="フェチバトル：理想個体マイナー")
    parser.add_argument("-val", type=int, default=7000)
    parser.add_argument("-cnt", type=int, default=3)
    parser.add_argument("-spd", type=int)
    parser.add_argument("-def", dest="df", type=int)
    parser.add_argument("-luk", type=int)
    parser.add_argument("-max", type=int, default=2000000)
    parser.add_argument("--lp", action="store_true", help="LP掲載用のHTMLを出力する")

    args = parser.parse_args()
    mine_units(args.val, args.cnt, args.spd, args.df, args.luk, args.max, args.lp)