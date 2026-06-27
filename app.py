from flask import Flask, render_template, request

def calculate_game_theory_ratio(off_pass, off_run, def_pass, def_run):
    """
    NFLの戦術的特性（パスのハイリスク・ハイリターン性、ランの手堅さ）
    を考慮して利得表を生成し、ナッシュ均衡を計算する
    """
    # リーグ平均の基準値
    NFL_PASS_AVG = 7.0
    NFL_RUN_AVG = 4.2

    # 1. リーグ平均からの乖離をベースに、対戦時の基準ヤードを算出（相乗効果）
    pass_base = (off_pass * def_pass) / NFL_PASS_AVG
    run_base = (off_run * def_run) / NFL_RUN_AVG

    # 2. アメフトのディフェンスの連動性を考慮した利得表（4パターン）の自動生成
    a = pass_base * 0.6  # Pass vs Pass (パス徹底警戒：パス不成功率が上がり大幅減)
    b = pass_base * 1.3  # Pass vs Run  (ラン警戒の裏：パスプロテクションが持ち、ロングパス成功)
    c = run_base * 1.2   # Run vs Pass  (パス警戒の裏：ニッケル/ダイム隊形で下がっている隙を突く)
    d = run_base * 0.7   # Run vs Run   (ラン徹底警戒：ボックスに8人詰め込まれてゲインストップ)

    # 3. ナッシュ均衡の分母を計算
    denominator = (a - b) - (c - d)

    if denominator == 0:
        return (50.0, 50.0), (50.0, 50.0)

    # 4. オフェンスの最適なパス比率 Pa
    off_pass_ratio = ((d - c) / denominator) * 100
    off_run_ratio = 100.0 - off_pass_ratio

    # 5. ディフェンスの最適なパス警戒比率 Pb
    def_pass_ratio = ((d - b) / denominator) * 100
    def_run_ratio = 100.0 - def_pass_ratio

    # 0%〜100%の間に収めるためのクリップ処理
    off_pass_ratio = max(0.0, min(100.0, off_pass_ratio))
    off_run_ratio = 100.0 - off_pass_ratio

    def_pass_ratio = max(0.0, min(100.0, def_pass_ratio))
    def_run_ratio = 100.0 - def_pass_ratio

    return (round(off_pass_ratio, 1), round(off_run_ratio, 1)), (round(def_pass_ratio, 1), round(def_run_ratio, 1))


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            off_pass = float(request.form.get("off_pass", "0"))
            off_run = float(request.form.get("off_run", "0"))
            def_pass = float(request.form.get("def_pass_allowed", "0"))
            def_run = float(request.form.get("def_run_allowed", "0"))

            off_ratio, def_ratio = calculate_game_theory_ratio(off_pass, off_run, def_pass, def_run)
            
            result = {
                "off_pass": off_ratio[0], "off_run": off_run[1],
                "def_pass": def_ratio[0], "def_run": def_ratio[1]
            }

        except ValueError:
            error = "数値を正しく入力してください。"

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)