def calculate_nash_and_scenarios(a, b, c, d):
    denominator = (a - b) - (c - d)
    
    # 分母が0の場合（純粋戦略へ）
    if denominator == 0:
        return handle_pure_strategy(a, b, c, d)

    pa = (d - c) / denominator
    pb = (d - b) / denominator

    # 混合戦略の計算（0 < p < 1 の範囲を優先）
    if 0 < pa < 1 and 0 < pb < 1:
        exp_yards = pa * (a * pb + b * (1.0 - pb)) + (1.0 - pa) * (c * pb + d * (1.0 - pb))
        return {
            "strategy": "Mixed Strategy",
            "off_pass": round(pa * 100, 1),
            "off_run": round((1.0 - pa) * 100, 1),
            "expected_yards": round(exp_yards, 1)
        }
    
    # 混合戦略にならない場合は純粋戦略
    return handle_pure_strategy(a, b, c, d)

def handle_pure_strategy(a, b, c, d):
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