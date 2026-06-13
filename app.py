from flask import Flask, render_template, request


def calculate_optimal_play_ratio(offense, defense):
    """
    対戦チームのスタッツから、最適なパス・ランの割合を計算する関数
    （元のロジックをそのまま使用）
    """
    pass_efficiency = offense["pass"] * defense["pass_allowed"]
    run_efficiency = offense["run"] * defense["run_allowed"]

    total_efficiency = pass_efficiency + run_efficiency

    if total_efficiency == 0:
        return 50.0, 50.0

    pass_ratio = (pass_efficiency / total_efficiency) * 100
    run_ratio = (run_efficiency / total_efficiency) * 100

    return round(pass_ratio, 1), round(run_ratio, 1)

# 1. Flaskの「本体」を立ち上げる
app = Flask(__name__)

# 2. トップページ（ / ）にアクセスされたときの動き
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            off_pass = float(request.form.get("off_pass", "0"))
            off_run = float(request.form.get("off_run", "0"))
            def_pass_allowed = float(request.form.get("def_pass_allowed", "0"))
            def_run_allowed = float(request.form.get("def_run_allowed", "0"))

            offense = {"pass": off_pass, "run": off_run}
            defense = {"pass_allowed": def_pass_allowed, "run_allowed": def_run_allowed}

            p_ratio, r_ratio = calculate_optimal_play_ratio(offense, defense)
            result = {"pass": p_ratio, "run": r_ratio}

        except ValueError:
            error = "数値を正しく入力してください。"

    return render_template("index.html", result=result, error=error)

# 3. おまじない（ローカルで実行したときだけ起動する）
if __name__ == "__main__":
    app.run(debug=True)