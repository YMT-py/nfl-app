from flask import Flask, render_template, request
import nfl_data_py as nfl
import pandas as pd
import numpy as np

app = Flask(__name__)

# NFL全32チームの略称リスト（ドロップダウン用）
NFL_TEAMS = sorted([
    'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
    'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
    'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
    'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
])

def get_team_stats_from_nfl_data(offense_team):
    """
    nfl_data_py から指定されたオフェンスチームの直近のpbp(Play-by-Play)データを取得し、
    対戦相手の守備傾向に応じた4つの平均獲得ヤード(a, b, c, d)を算出する
    """
    try:
        # 2025年シーズンのデータを取得
        df_pbp = nfl.import_pbp_data([2025])
        
        # 該当チームの攻撃プレイ、かつパスかランのみに絞り込む
        df_team = df_pbp[
            (df_pbp['postfix_team'] == offense_team) & 
            (df_pbp['play_type'].isin(['pass', 'run'])) &
            (df_pbp['yards_gained'].notna())
        ].copy()
        
        if df_team.empty:
            return None
            
        # ディフェンスの警戒度を「ディフェンスのボックス人数(defenders_in_box)」で判定
        # 7人以上＝ラン警戒(Run Contain) / 6人以下＝パス警戒(Pass Cover)
        df_team['def_alignment'] = np.where(df_team['defenders_in_box'] >= 7, 'run_contain', 'pass_cover')
        
        # 4つのシナリオの平均ヤードを計算
        a = df_team[(df_team['play_type'] == 'pass') & (df_team['def_alignment'] == 'pass_cover')]['yards_gained'].mean()
        b = df_team[(df_team['play_type'] == 'pass') & (df_team['def_alignment'] == 'run_contain')]['yards_gained'].mean()
        c = df_team[(df_team['play_type'] == 'run') & (df_team['def_alignment'] == 'pass_cover')]['yards_gained'].mean()
        d = df_team[(df_team['play_type'] == 'run') & (df_team['def_alignment'] == 'run_contain')]['yards_gained'].mean()
        
        # データ不足時の補正
        a = round(a, 1) if not pd.isna(a) else 4.0
        b = round(b, 1) if not pd.isna(b) else 10.0
        c = round(c, 1) if not pd.isna(c) else 5.5
        d = round(d, 1) if not pd.isna(d) else 2.5
        
        return a, b, c, d
    except Exception as e:
        print(f"Error fetching data: {e}")
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

    # 修正前の数式のままパーセンテージに変換
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
        "expected_yards": round(exp_yards, 1)
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
                stats = get_team_stats_from_nfl_data(team)
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