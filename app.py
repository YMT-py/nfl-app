from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

# NFL全32チームの略称リスト
NFL_TEAMS = sorted([
    'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
    'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
    'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
    'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
])

def load_team_stats_json(offense_team):
    """
    事前集計済みの軽量JSONファイルからチームのスタッツ(a, b, c, d)を読み込む。
    メモリを一切消費せず、一瞬で処理が完了します。
    """
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'nfl_stats_2025.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            stats_dict = json.load(f)
        
        if offense_team in stats_dict:
            return stats_dict[offense_team] # [a, b, c, d] のリストが返る
    except Exception as e:
        print(f"Error loading JSON: {e}")
    return None

def calculate_nash_and_scenarios(a, b, c, d):
    """
    混合戦略の均衡を最優先で計算し、それが成立しない場合（支配戦略がある場合）のみ
    純粋戦略の均衡を返す計算ロジック
    """
    # 利得マトリクス
    #        | Pass守備(pb) | Run守備(1-pb)
    # Pass(pa)|     a        |      b
    # Run(1-pa)|     c        |      d
    
    denominator = (a - b) - (c - d)
    
    # 0除算対策: 分母が0の場合は純粋戦略へ
    if denominator == 0:
        return handle_pure_strategy(a, b, c, d)

    # ナッシュ均衡の基本式
    pa = (d - c) / denominator
    pb = (d - b) / denominator

    # 1. 混合戦略の判定 (0 < p < 1)
    # ここで「パスのみ」「ランのみ」に固定せず、駆け引きの比率を優先して計算する
    if 0 < pa < 1 and 0 < pb < 1:
        exp_yards = pa * (a * pb + b * (1.0 - pb)) + (1.0 - pa) * (c * pb + d * (1.0 - pb))
        
        return {
            "strategy": "Mixed Strategy",
            "off_pass": round(pa * 100, 1),
            "off_run": round((1.0 - pa) * 100, 1),
            "def_pass": round(pb * 100, 1),
            "def_run": round((1.0 - pb) * 100, 1),
            "p_pass_pass": round(pa * pb * 100, 1),
            "p_pass_run": round(pa * (1.0 - pb) * 100, 1),
            "p_run_pass": round((1.0 - pa) * pb * 100, 1),
            "p_run_run": round((1.0 - pa) * (1.0 - pb) * 100, 1),
            "expected_yards": round(exp_yards, 1)
        }
    
    # 2. 混合戦略が成立しない場合（確率が範囲外）は純粋戦略へ
    return handle_pure_strategy(a, b, c, d)

def handle_pure_strategy(a, b, c, d):
    """
    純粋戦略（支配戦略）の探索ロジック
    """
    # マクシミン戦略: オフェンスが選んだプレイに対し、ディフェンスが最適に守った場合の最悪利得を比較
    min_if_pass = min(a, b)
    min_if_run = min(c, d)

    if min_if_pass >= min_if_run:
        # パスが支配的
        return {
            "strategy": "Pure Strategy (Pass Dominated)",
            "off_pass": 100.0, "off_run": 0.0,
            "def_pass": 100.0, "def_run": 0.0,
            "p_pass_pass": 100.0, "p_pass_run": 0.0,
            "p_run_pass": 0.0, "p_run_run": 0.0,
            "expected_yards": float(min(a, b))
        }
    else:
        # ランが支配的
        return {
            "strategy": "Pure Strategy (Run Dominated)",
            "off_pass": 0.0, "off_run": 100.0,
            "def_pass": 0.0, "def_run": 100.0,
            "p_pass_pass": 0.0, "p_pass_run": 0.0,
            "p_run_pass": 0.0, "p_run_run": 100.0,
            "expected_yards": float(min(c, d))
        }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    
    form_data = {"gain_a": "", "gain_b": "", "gain_c": "", "gain_d": "", "selected_team": ""}

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "clear":
            return render_template("index.html", result=result, error=error, teams=NFL_TEAMS, form_data=form_data)
            
        elif action == "fetch_stats":
            team = request.form.get("team_select")
            if team:
                stats = load_team_stats_json(team)
                if stats:
                    form_data["gain_a"], form_data["gain_b"], form_data["gain_c"], form_data["gain_d"] = stats
                    form_data["selected_team"] = team
                else:
                    error = f"Could not retrieve stats for team: {team}"
            else:
                error = "Please select a team first."

        elif action == "calculate":
            try:
                form_data["gain_a"] = request.form.get("gain_a", "0")
                form_data["gain_b"] = request.form.get("gain_b", "0")
                form_data["gain_c"] = request.form.get("gain_c", "0")
                form_data["gain_d"] = request.form.get("gain_d", "0")
                form_data["selected_team"] = request.form.get("selected_team", "")

                a = float(form_data["gain_a"])
                b = float(form_data["gain_b"])
                c = float(form_data["gain_c"])
                d = float(form_data["gain_d"])

                result = calculate_nash_and_scenarios(a, b, c, d)
            except ValueError:
                error = "Invalid input. Please enter valid numeric values for all fields."

    return render_template("index.html", result=result, error=error, teams=NFL_TEAMS, form_data=form_data)

if __name__ == "__main__":
    app.run(debug=True)