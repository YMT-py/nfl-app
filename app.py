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
    try:
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'nfl_stats_2025.json'))
        with open(json_path, 'r', encoding='utf-8') as f:
            stats_dict = json.load(f)
        if offense_team in stats_dict:
            return stats_dict[offense_team]
    except Exception as e:
        print(f"Error loading JSON: {e}")
    return None

def handle_pure_strategy(a, b, c, d):
    """純粋戦略（支配戦略）の探索ロジック"""
    if min(a, b) >= min(c, d):
        return {
            "strategy": "Pure Strategy (Pass Dominated)",
            "off_pass": 100.0, "off_run": 0.0,
            "expected_yards": float(min(a, b))
        }
    else:
        return {
            "strategy": "Pure Strategy (Run Dominated)",
            "off_pass": 0.0, "off_run": 100.0,
            "expected_yards": float(min(c, d))
        }

def calculate_nash_and_scenarios(a, b, c, d):
    """
    混合戦略を優先し、成立しない場合にのみ純粋戦略を返すロジック
    """
    denominator = (a - b) - (c - d)

    # 1. 混合戦略の計算 (ガード処理なし)
    if denominator != 0:
        pa = (d - c) / denominator
        pb = (d - b) / denominator
        
        # 混合戦略が数学的に成立する範囲(0 < p < 1)ならそれを採用
        if 0 < pa < 1 and 0 < pb < 1:
            exp_yards = pa * (a * pb + b * (1.0 - pb)) + (1.0 - pa) * (c * pb + d * (1.0 - pb))
            
            return {
                "strategy": "Mixed Strategy",
                "off_pass": round(pa * 100, 1),
                "off_run": round((1.0 - pa) * 100, 1),
                "def_pass": round(pb * 100, 1),
                "def_run": round((1.0 - pb) * 100, 1),
                "expected_yards": round(exp_yards, 1)
            }

    # 2. 混合戦略が成立しない（範囲外）場合は純粋戦略へ分岐
    return handle_pure_strategy(a, b, c, d)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    form_data = {"gain_a": "", "gain_b": "", "gain_c": "", "gain_d": "", "selected_team": ""}
    error = None

    if request.method == 'POST':
        action = request.form.get("action")
        if action == "fetch_stats":
            team = request.form.get("team_select")
            stats = load_team_stats_json(team)
            if stats:
                form_data.update({"gain_a": str(stats[0]), "gain_b": str(stats[1]), 
                                  "gain_c": str(stats[2]), "gain_d": str(stats[3]), "selected_team": team})
        elif action == "calculate":
            try:
                a, b, c, d = float(request.form.get("gain_a")), float(request.form.get("gain_b")), \
                             float(request.form.get("gain_c")), float(request.form.get("gain_d"))
                result = calculate_nash_and_scenarios(a, b, c, d)
                form_data.update({"gain_a": str(a), "gain_b": str(b), "gain_c": str(c), "gain_d": str(d)})
            except ValueError:
                error = "Invalid input values."

    return render_template('index.html', teams=NFL_TEAMS, form_data=form_data, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)