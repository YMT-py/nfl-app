from flask import Flask, render_template, request

def calculate_optimal_play_ratio(offense, defense):
    """
    ゲーム理論（混合戦略ナッシュ均衡）に基づいた
    オフェンス・ディフェンス両チームの最適比率計算
    """
    a = offense["pass"]           # Pass vs Pass (例: 3)
    b = offense["run"]            # Pass vs Run (例: 15)
    c = defense["pass_allowed"]   # Run vs Pass (例: 8)
    d = defense["run_allowed"]    # Run vs Run  (例: 2)

    # 共通の分母
    denominator = (a - b) - (c - d)

    # 安全対策：分母が0の場合は50%ずつにする
    if denominator == 0:
        return (50.0, 50.0), (50.0, 50.0)

    # 1. オフェンスの最適なパス比率 Pa
    off_pass_ratio = ((d - c) / denominator) * 100
    off_run_ratio = 100.0 - off_pass_ratio

    # 2. ディフェンスの最適なパス警戒比率 Pb
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
            a = float(request.form.get("off_pass", "0"))
            b = float(request.form.get("off_run", "0"))
            c = float(request.form.get("def_pass_allowed", "0"))
            d = float(request.form.get("def_run_allowed", "0"))

            offense = {"pass": a, "run": b}
            defense = {"pass_allowed": c, "run_allowed": d}

            off_ratio, def_ratio = calculate_optimal_play_ratio(offense, defense)
            
            # 結果の辞書にディフェンス側も追加
            result = {
                "off_pass": off_ratio[0], "off_run": off_ratio[1],
                "def_pass": def_ratio[0], "def_run": def_ratio[1]
            }

        except ValueError:
            error = "数値を正しく入力してください。"

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)