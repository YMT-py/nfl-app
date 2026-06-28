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
    修正前の純粋な計算ロジック（変更なし）
    """
    denominator = (a - b) - (c - d)

    if denominator == 0:
        exp_yards = (a + b + c + d) / 4.0
        return {
            "off_pass": 50.0, "off_run": 50.0,
            "def_pass": 50.0, "def_run": 50.0,
            "p_pass_pass": 25.0, "p_pass_run": 25.0,
            "p_run_pass": 25.0, "p_run_run": 25.0,
            "expected_yards": round(exp_yards, 1)
        }

    off_pass_ratio = ((d - c) / denominator) * 100
    off_run_ratio = 100.0 - off_pass_ratio

    def_pass_ratio = ((d - b) / denominator) * 100
    def_run_ratio = 100.0 - def_pass_ratio

    pa = off_pass_ratio / 100.0
    pb = def_pass_ratio / 100.0

    p_pass_pass = pa * pb * 100
    p_pass_run  = pa * (1 - pb) * 100
    p_run_pass  = (1 - pa) * pb * 100
    p_run_run   = (1 - pa) * (1 - pb) * 100

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
        "expected_watts" if False else "expected_yards": round(exp_yards, 1)
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