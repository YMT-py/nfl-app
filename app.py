Python
def calculate_optimal_play_ratio(offense, defense):
    """
    1プレーあたりの効率性（Yards per Play）をベースにした新しい計算ロジック
    """
    # 1. チームAの1プレーあたり獲得ヤード × チームBの1プレーあたり許容ヤード で効率性を計算
    pass_efficiency = offense["pass"] * defense["pass_allowed"]
    run_efficiency = offense["run"] * defense["run_allowed"]

    total_efficiency = pass_efficiency + run_efficiency

    # 安全対策：分母が0になった場合は50%ずつにする
    if total_efficiency == 0:
        return 50.0, 50.0

    # 2. 合計効率性から、パスとランの最適な比率をパーセンテージで算出
    pass_ratio = (pass_efficiency / total_efficiency) * 100
    run_ratio = (run_efficiency / total_efficiency) * 100

    return round(pass_ratio, 1), round(run_ratio, 1)