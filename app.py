from flask import Flask, render_template, request

def calculate_nash_and_scenarios(a, b, c, d):
    """
    ユーザーが入力した4つの利得（a, b, c, d）から
    混合戦略ナッシュ均衡と、4パターンの発生確率を計算する
    """
    # 一次条件の解を導くための分母
    # 提示例: (3 - 15) - (8 - 2) = -12 - 6 = -18
    denominator = (a - b) - (c - d)

    if denominator == 0:
        # 分母が0（極端なデータ）の場合は均等配分を返す
        return {
            "off_pass": 50.0, "off_run": 50.0,
            "def_pass": 50.0, "def_run": 50.0,
            "p_pass_pass": 25.0, "p_pass_run": 25.0,
            "p_run_pass": 25.0, "p_run_run": 25.0
        }

    # 1. オフェンスの最適なパス比率 Pa
    # 提示例: (2 - 8) / -18 = -6 / -18 = 1/3 (33.3%)
    off_pass_ratio = ((d - c) / denominator)
    off_pass_ratio = max(0.0, min(100.0, off_pass_ratio * 100))
    off_run_ratio = 100.0 - off_pass_ratio

    # 2. ディフェンスの最適なパス警戒比率 Pb
    # 提示例: (2 - 15) / -18 = -13 / -18 = 13/18 (72.2%)
    def_pass_ratio = ((d - b) / denominator)
    def_pass_ratio = max(0.0, min(100.0, def_pass_ratio * 100))
    def_run_ratio = 100.0 - def_pass_ratio

    # 3. 4つのシチュエーションがそれぞれ発生する確率（交差確率）
    pa = off_pass_ratio / 100.0
    pb = def_pass_ratio / 100.0

    p_pass_pass = pa * pb * 100          # Pass vs Pass (例: 1/3 * 13/18 = 13/54)
    p_pass_run  = pa * (1 - pb) * 100    # Pass vs Run  (例: 1/3 *  5/18 =  5/54)
    p_run_pass  = (1 - pa) * pb * 100    # Run vs Pass  (例: 2/3 * 13/18 = 26/54)
    p_run_run   = (1 - pa) * (1 - pb) * 100  # Run vs Run   (例: 2/3 *  5/18 = 10/54)

    return {
        "off_pass": round(off_pass_ratio, 1),
        "off_run": round(off_run_ratio, 1),
        "def_pass": round(def_pass_ratio, 1),
        "def_run": round(def_run_ratio, 1),
        "p_pass_pass": round(p_pass_pass, 1),
        "p_pass_run": round(p_pass_run, 1),
        "p_run_pass": round(p_run_pass, 1),
        "p_run_run": round(p_run_run, 1)
    }

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            # 4つの利得表の値を直接取得
            a = float(request.form.get("gain_a", "0"))
            b = float(request.form.get("gain_b", "0"))
            c = float(request.form.get("gain_c", "0"))
            d = float(request.form.get("gain_d", "0"))

            result = calculate_nash_and_scenarios(a, b, c, d)

        except ValueError:
            error = "Please enter valid numeric values."

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)