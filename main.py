import flet as ft
import hashlib
import base64
import asyncio
import random

async def main(page: ft.Page):
    page.title = "フェチバトル: デュエル"
    page.padding = 10
    # スマホの画面幅いっぱいに使う設定
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    page.fonts = {
        "Digital": "https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap",
        "Dot": "https://fonts.googleapis.com/css2?family=Silkscreen&display=swap"
    }

    players = [
        {"data": None, "ui": None},
        {"data": None, "ui": None}
    ]

    battle_log = ft.Column(spacing=5)
    
    battle_button = ft.FilledButton(
        "BATTLE START!", 
        visible=False, 
        width=200, 
        height=50,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED)
    )

    # --- ロジック層 ---

    def get_stats_from_seed(seed):
        """シード値（HEX文字列）からステータスを確定的に生成"""
        hp = int(seed[0:4], 16) % 5000 + 3000
        atk = int(seed[4:8], 16) % 1000 + 500
        def_val = int(seed[12:16], 16) % 300 + 100
        spd = int(seed[8:12], 16) % 100 + 10
        luk = int(seed[16:20], 16) % 20 + 5
        
        material_val = int(seed[10:13], 16) % 255
        if material_val < 50:
            m, col = "漆黒 of ラバー", ft.Colors.AMBER_ACCENT_200
        elif material_val < 110:
            m, col = "至高 of スキン", ft.Colors.ORANGE_200
        elif material_val < 170:
            m, col = "伝統 of スク水 / 制服", ft.Colors.BLUE_800
        elif material_val < 230:
            m, col = "聖なるシルク / ナース", ft.Colors.WHITE
        else:
            m, col = "未知の魔導素材", ft.Colors.GREY_400
        
        return {
            "hp": hp, "max_hp": hp, "atk": atk, "def": def_val, 
            "spd": spd, "luk": luk, "material": m, "color": col, 
            "seed": seed[:20] # 通信用の短いシード
        }

    def generate_identicon(seed_str, color):
        """シード値から9x9の対称形アイコンを生成"""
        # グローバルな random ではなく、この関数専用のランダム生成器を作る
        local_random = random.Random(seed_str)
        
        cells = []
        for y in range(9):
            # 1行の左側5マスをランダムに決定
            row_half = [random.choice([True, False]) for _ in range(5)]
            # 右側4マスを鏡合わせにする (0,1,2,3,4,3,2,1,0)
            row_full = row_half + row_half[-2::-1]
            cells.extend(row_full)

        return ft.Container(
            content=ft.GridView(
                runs_count=9,
                max_extent=14, # 140px / 9マス ≒ 15px
                spacing=1,
                run_spacing=1,
                controls=[
                    ft.Container(
                        bgcolor=color if is_on else ft.Colors.BLACK,
                        border_radius=1
                    ) for is_on in cells
                ],
            ),
            width=140,
            height=140,
            padding=5,
            bgcolor="black",
            border_radius=5,
            border=ft.Border.all(1, ft.Colors.WHITE10)
        )

    # --- ヘルパー: ステータス表示の更新 ---
    def update_stat_display(ui_container, data):
        # create_card内のColumnの構造に合わせてインデックスを修正
        # [0] FilledButton ("画像で読み込み") <- 追加されたので1つずれた
        # [1] Text ("UNIT 1")
        # [2] load_header
        # [3] Divider
        # [4] Image / Identicon
        # [5] Text ("WAITING...")
        # [6] stat_row (←ここを取得したい)
        
        stat_row = ui_container.content.controls[6] # 5から6に変更
        stats = ["hp", "atk", "def", "spd", "luk"]
        for i, key in enumerate(stats):
            stat_row.controls[i].content.controls[1].value = str(data[key])
        # カード単位で更新
        ui_container.update()


    async def log_add_animated(text, color):
        new_log = ft.Text("", color=color, weight="bold", font_family="Digital")
        battle_log.controls.insert(0, new_log)
        display_text = ""
        for char in text:
            display_text += char
            new_log.value = display_text
            page.update()
            await asyncio.sleep(0.01)

    async def run_battle(e):
        battle_button.disabled = True
        battle_log.controls.clear()
        p1_data, p2_data = players[0]["data"], players[1]["data"]
        p1_ui, p2_ui = players[0]["ui"], players[1]["ui"]
        p1_data["hp"], p2_data["hp"] = p1_data["max_hp"], p2_data["max_hp"]
        
        update_stat_display(p1_ui, p1_data)
        update_stat_display(p2_ui, p2_data)
        await log_add_animated("── BATTLE START ──", ft.Colors.YELLOW)
        
        current_turn = 1
        while p1_data["hp"] > 0 and p2_data["hp"] > 0:
            turn_color = ft.Colors.CYAN_300 if current_turn % 2 == 1 else ft.Colors.ORANGE_200
            await log_add_animated(f"-- ターン {current_turn} --", turn_color)
            current_turn += 1

            if p1_data["spd"] + random.randint(0, 20) >= p2_data["spd"] + random.randint(0, 20):
                turn_order = [(p1_data, p2_data, p2_ui, "UNIT 1"), (p2_data, p1_data, p1_ui, "UNIT 2")]
            else:
                turn_order = [(p2_data, p1_data, p1_ui, "UNIT 2"), (p1_data, p2_data, p2_ui, "UNIT 1")]

            for attacker, defender, def_ui, attacker_name in turn_order:
                if attacker["hp"] <= 0 or defender["hp"] <= 0: continue

                base_dmg = int(attacker["atk"] * random.uniform(0.9, 1.2))
                dmg = max(1, base_dmg - defender["def"])
                log_msg, effect_color = f"{attacker_name}: 攻撃！", attacker["color"]

                if random.randint(1, 100) <= attacker["luk"]:
                    dmg, log_msg, effect_color = int(dmg * 1.5), f"{attacker_name}:★会心！", ft.Colors.ORANGE_600
                elif random.randint(1, 100) <= defender["luk"]:
                    dmg, log_msg, effect_color = max(1, int(dmg * 0.2)), f"{attacker_name}:★ガード！", ft.Colors.CYAN_300

                defender["hp"] -= dmg
                if defender["hp"] < 0: defender["hp"] = 0
                update_stat_display(def_ui, defender)
                await log_add_animated(f"{log_msg} {dmg} DMG", effect_color)

                def_ui.border = ft.Border.all(3, effect_color)
                await asyncio.sleep(0.3)
                def_ui.border = ft.Border.all(1, ft.Colors.WHITE24)
                page.update()

                if defender["hp"] <= 0:
                    await log_add_animated(f"── {attacker_name} WIN! ──", ft.Colors.RED_ACCENT)
                    break

        battle_button.disabled = False
        page.update()

    # --- インターフェース層 ---

    async def handle_pick(idx):
        files = await ft.FilePicker().pick_files(file_type=ft.FilePickerFileType.IMAGE, with_data=True)
        if not files or not files[0].bytes: return
        
        seed = hashlib.sha256(files[0].bytes).hexdigest()
        res = get_stats_from_seed(seed)
        players[idx]["data"] = res
        
        img_base64 = base64.b64encode(files[0].bytes).decode()
        ui = players[idx]["ui"]
        
        # UIの更新
        # ui.content.controls[4].src = f"data:image/png;base64,{img_base64}"
        # ui.content.controls[4].opacity = 1.0  # 透明度を戻す（重要！）
        # ui.content.controls[5].value = res["material"]
        # ui.content.controls[5].color = res["color"]

        # 既存の controls[4] が Image か Identicon かに関わらず、新しい Image インスタンスで上書きする
        ui.content.controls[4] = ft.Image(
            src=f"data:image/png;base64,{img_base64}",
            width=140, 
            height=140, 
            opacity=1.0,
            fit=ft.BoxFit.CONTAIN,
        )
        
        # ほかの情報の更新
        ui.content.controls[5].value = res["material"]
        ui.content.controls[5].color = res["color"]

        # ボタンの更新
        target_text_button = ui.content.controls[7]
        
        target_text_button.content.controls[1].value = f"CODE: {res['seed']}"
        target_text_button.content.controls[1].color = ft.Colors.BLUE_200

        # ステータス表示の更新（ここは前回直した controls[6] になっているはず）
        update_stat_display(ui, res)

        # 両方揃ったらバトルボタンを表示
        if players[0]["data"] and players[1]["data"]:
            battle_button.visible = True
            battle_button.update() # ボタン単体を即座に更新
            
        # ここでページ全体を更新！
        # await page.update_async() if hasattr(page, "update_async") else page.update()
        page.update()


    async def load_by_code(idx, code_str):
        if len(code_str) < 20: return
        res = get_stats_from_seed(code_str)
        players[idx]["data"] = res
        
        ui = players[idx]["ui"]
        new_icon = generate_identicon(res["seed"], res["color"])
        ui.content.controls[4] = new_icon # Image(3)の次なので 4

        target_title = ui.content.controls[5] # Text("WAITING...") の場所なので 5
        target_text_button = ui.content.controls[7] # code_display の場所なので 7

        target_title.value = f"{res['material']}"
        target_title.color = res["color"]
        
        # ここを修正！
        target_text_button.content.controls[1].value = f"CODE: {res['seed']}"
        target_text_button.content.controls[1].color = ft.Colors.WHITE
        
        update_stat_display(ui, res)
        # await page.update_async() if hasattr(page, "update_async") else page.update()
        # コード入力時も「両方揃ったか」チェックする
        if players[0]["data"] and players[1]["data"]:
            battle_button.visible = True
            battle_button.update()

        page.update()



    # --- UIパーツ: ステータスパネル ---
    def stat_panel(label, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=9, color=color, font_family="Dot"),
                ft.Text(value, size=14, color=color, font_family="Digital"),
            ], spacing=0, horizontal_alignment="center"),
            bgcolor="black", padding=5, border_radius=5, 
            expand=True, # 親のRowの中で均等に広がるようにする
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, color))
        )
    
    async def copy_code(code_str):
        if code_str and "----" not in code_str:
            try:
                # サンプルサイトの方式：ft.Clipboard() インスタンスを作成して set する
                await ft.Clipboard().set(code_str)
                
                # ユーザーへのフィードバック
                page.snack_bar = ft.SnackBar(ft.Text(f"コードをコピーしました: {code_str}"))
                page.snack_bar.open = True
            except Exception as e:
                print(f"Clipboard Error: {e}")
                # 万が一上記でダメな場合、page.set_clipboard_data を試す古い習慣も残しておく
                # （バージョン混在対策）
            
            page.update()

    async def paste_and_load(idx, e):
        # クリップボードから取得
        code = await ft.Clipboard().get()
        if code:
            # 入力フィールドを探して値をセット（視覚的なフィードバック）
            # load_header -> controls[1] がTextField
            e.control.parent.controls[1].value = code
            page.update()
            # ロード実行
            await load_by_code(idx, code)

    # --- UIパーツ: カード生成 ---
    def create_card(idx):
        stat_row = ft.Row([
            stat_panel("HP", "0", "greenaccent"),
            stat_panel("ATK", "0", "redaccent"),
            stat_panel("DEF", "0", "blueaccent"),
            stat_panel("SPD", "0", "amberaccent"),
            stat_panel("LUK", "0", "purpleaccent")
        ], spacing=4, alignment="center")

        load_header = ft.Row([
            ft.IconButton(ft.Icons.ADD_A_PHOTO_ROUNDED, icon_color="cyan", on_click=lambda _: asyncio.create_task(handle_pick(idx))),
            ft.TextField(label="コード", width=200, height=30, text_size=10, on_submit=lambda e: asyncio.create_task(load_by_code(idx, e.control.value))),
            ft.IconButton(ft.Icons.ASSIGNMENT_RETURN_ROUNDED, icon_color="grey", icon_size=18, on_click=lambda e: asyncio.create_task(paste_and_load(idx, e))),
        ], alignment="center", spacing=0)

        # create_card 関数内
        code_display = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.COPY, size=16),
                ft.Text("CODE: ----", color=ft.Colors.GREY_400) # [1]番目の要素
            ], alignment="center", spacing=5),
            on_click=lambda e: asyncio.create_task(copy_code(e.control.content.controls[1].value.replace("CODE: ", "")))
        )

        return ft.Container(
            padding=10, bgcolor=ft.Colors.GREY_900,
            border=ft.Border.all(1, ft.Colors.WHITE24), border_radius=10,
            content=ft.Column([
                ft.FilledButton("画像で読み込み", on_click=lambda _: asyncio.create_task(handle_pick(idx))),
                ft.Text(f"UNIT {idx+1}", size=12, color="grey", font_family="Dot"), # [0]
                load_header, # [1]
                ft.Divider(height=1, color="white10"), # [2]
                ft.Image(src="https://flet.dev/img/pages/getting-started/icon.png", width=140, height=140, opacity=0.3), # [3]
                ft.Text("WAITING...", size=16, weight="bold", font_family="Dot"), # [4]
                stat_row, # [5]
                code_display, # [6]
            ], horizontal_alignment="center", spacing=10)
        )


    # 初期化
    players[0]["ui"] = create_card(0)
    players[1]["ui"] = create_card(1)
    battle_button.on_click = run_battle

    page.add(
        ft.Text("フェチバトル: デュエル", size=24, weight="black"),
        ft.ResponsiveRow([
            ft.Column([players[0]["ui"]], col={"sm": 12, "md": 5}),
            ft.Column([ft.Text("VS", size=20, weight="bold")], col={"sm": 12, "md": 2}, horizontal_alignment="center"),
            ft.Column([players[1]["ui"]], col={"sm": 12, "md": 5}),
        ], alignment="center", vertical_alignment="center"),
        ft.Divider(height=20, color="transparent"),
        battle_button,
        ft.Container(
            content=battle_log, height=180, 
            width=450, # width固定を解除してmax_widthに
            bgcolor="black", padding=10, border_radius=5
        )
    )

if __name__ == "__main__":
    ft.run(main)