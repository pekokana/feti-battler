import hashlib
import random
import sys  # 追加

def mine_strong_units(target_sum, num_results):
    print(f"--- 探索開始 (目標合計値: {target_sum} 以上 / 必要件数: {num_results}) ---")
    
    found_count = 0
    count = random.randint(0, 10000000)
    results = []

    while found_count < num_results:
        seed = hashlib.sha256(str(count).encode()).hexdigest()[:20]
        
        # ステータス計算ロジック
        hp = int(seed[0:4], 16) % 5000 + 3000
        atk = int(seed[4:8], 16) % 1000 + 500
        
        current_sum = hp + atk
        
        if current_sum >= target_sum:
            found_count += 1
            print(f"\n[{found_count}] 発見! Code: {seed} (HP:{hp} ATK:{atk} SUM:{current_sum})")
            results.append(seed)
        
        count += 1
        if count % 100000 == 0:
            print(".", end="", flush=True)

    print(f"\n--- 完了 ---")
    return results

if __name__ == "__main__":
    # --- 実行時パラメータの受け取り ---
    # デフォルト値を設定（引数が足りない場合用）
    target = 6500
    count_to_find = 3

    try:
        if len(sys.argv) > 1:
            target = int(sys.argv[1])
        if len(sys.argv) > 2:
            count_to_find = int(sys.argv[2])
    except ValueError:
        print("引数は数値で入力してください。例: uv run mine.py 7000 5")
        sys.exit(1)

    mine_strong_units(target, count_to_find)