def calculate_nash_and_scenarios(a, b, c, d):
    """
    ナッシュ均衡とシナリオ確率を計算する関数。
    計算結果が 0%〜100% の範囲を超えた場合、自動的に純粋戦略（ガード機能）へ切り替えます。
    """
    denominator = (a - b) - (c - d)

    # 分母が0（完全に並行な利得）の場合のセーフティ
    if denominator == 0:
        exp_yards = (a + b + c + d) / 4.0
        return {
            "off_pass": 50.0, "off_run": 50.0,
            "def_pass": 50.0, "def_run": 50.0,
            "p_pass_pass": 25.0, "p_pass_run": 25.0,
            "p_run_pass": 25.0, "p_run_run": 25.0,
            "expected_yards": round(exp_yards, 1)
        }

    # 一次条件から確率を計算 (0〜100ではなく、0.0〜1.0 の比率として算出)
    pa = (d - c) / denominator  # オフェンスのパス比率
    pb = (d - b) / denominator  # ディフェンスのパス警戒比率

    # 🛡️ ガード機能：確率が 0.0 未満、または 1.0 を超えた場合の丸め処理
    # これにより、実データ（支配戦略）の時でも 100% や 0% に綺麗に収まります
    pa = max(0.0, min(1.0, pa))
    pb = max(0.0, min(1.0, pb))

    # パーセンテージ表記に変換
    off_pass_ratio = pa * 100
    off_run_ratio = (1.0 - pa) * 100
    def_pass_ratio = pb * 100
    def_run_ratio = (1.0 - pb) * 100

    # 各戦術がぶつかる「同時確率」を計算 (足して100%になる)
    p_pass_pass = pa * pb * 100
    p_pass_run  = pa * (1.0 - pb) * 100
    p_run_pass  = (1.0 - pa) * pb * 100
    p_run_run   = (1.0 - pa) * (1.0 - pb) * 100

    # 期待獲得ヤードの計算
    exp_yards = pa * (a * pb + b * (1.0 - pb)) + (1.0 - pa) * (c * pb + d * (1.0 - pb))

    return {
        "off_pass": round(off_pass_ratio, 1),
        "off_run": round(off_run_ratio, 1),
        "def_pass": round(def_pass_ratio, 1),
        "def_run": round(def_run_ratio, 1),
        "p_pass_pass": round(p_pass_pass, 1),
        "p_pass_run": round(p_pass_run, 1),
        "p_run_pass": round(p_run_pass, 1),
        "p_run_run": round(p_run_run, 1),
        "expected_yards": round(exp_yards, 1)
    }