from flask import Flask, render_template, request

def calculate_nash_and_scenarios(a, b, c, d):
    """
    ユーザーが入力した4つの利得（a, b, c, d）から
    混合戦略ナッシュ均衡、4パターンの発生確率、および期待獲得ヤードを計算する
    """
    denominator = (a - b) - (c - d)

    if denominator == 0:
        # 分母が0の場合は単純平均
        exp_yards = (a + b + c + d) / 4.0
        return {
            "off_pass": 50.0, "off_run": 50.0,
            "def_pass": 50.0, "def_run": 50.0,
            "p_pass_pass": 25.0, "p_pass_run": 25.0,
            "p_run_pass": 25.0, "p_run_run": 25.0,
            "expected_yards": round(exp_yards, 1)
        }

    off_pass_ratio = ((d - c) / denominator)
    off_pass_ratio = max(0.0, min(100.0, off_pass_ratio * 100))
    off_run_ratio = 100.0 - off_pass_ratio

    def_pass_ratio = ((d - b) / denominator)
    def_pass_ratio = max(0.0, min(100.0, def_pass_ratio * 100))
    def_run_ratio = 100.0 - def_pass_ratio

    pa = off_pass_ratio / 100.0
    pb = def_pass_ratio / 100.0

    p_pass_pass = pa * pb * 100
    p_pass_run  = pa * (1 - pb) * 100
    p_run_pass  = (1 - pa) * pb * 100
    p_run_run   = (1 - pa) * (1 - pb) * 100

    # 🏈 期待獲得ヤード数（Expected Value）の計算
    # 均衡状態では、どのルートで計算しても同じ値に収束します
    exp_yards = pa * (a * pb + b * (1 - pb)) + (1 - pa) * (c * pb + d * (1 - pb))

    return {
        "off_pass": round(off_pass_ratio, 1),
        "off_run": round(off_run_ratio, 1),
        "def_pass": round(def_pass_ratio, 1),
        "def_run": round(def_run_ratio, 1),
        "p_pass_pass": round(p_pass_pass, 1),
        "p_pass_run": round(p_pass_run, 1),
        "p_run_pass": round(p_run_pass, 1),
        "p_run_run": round(p_run_run, 1),
        "expected_yards": round(exp_yards, 1) # 追加
    }

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            a = float(request.form.get("gain_a", "0"))
            b = float(request.form.get("gain_b", "0"))
            c = float(request.form.get("gain_c", "0"))
            d = float(request.form.get("gain_d", "0"))

            result = calculate_nash_and_scenarios(a, b, c, d)

        except ValueError:
            error = "Invalid input. Please enter valid numeric values for all fields."

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)