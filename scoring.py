from config import *

# ==========================
# 市场评分（100分）
# ==========================

def calculate_score(
    drawdown,
    vix,
    rsi,
    fear_greed,
    mega_caps,
    premarket
):

    score = 50

    # ATH回撤（核心）

    if drawdown <= -30:
        score += 30

    elif drawdown <= -20:
        score += 20

    elif drawdown <= -10:
        score += 10

    elif drawdown <= -5:
        score += 5

    # VIX

    if vix >= 35:
        score += 15

    elif vix >= 25:
        score += 10

    elif vix >= 20:
        score += 5

    # RSI

    if rsi < 30:
        score += 10

    elif rsi < 40:
        score += 5

    # Fear & Greed

    if fear_greed is not None:

        if fear_greed < 20:
            score += 10

        elif fear_greed < 40:
            score += 5

    # 权重股

    if mega_caps <= -4:
        score += 15

    elif mega_caps <= -2:
        score += 8

    # 盘前

    if premarket <= -2:
        score += 10

    elif premarket <= -1:
        score += 5

    return min(score, 100)


# ==========================
# 评分对应倍率
# ==========================

def score_to_multiplier(score):

    if score >= 90:
        return 2.5

    elif score >= 80:
        return 2.0

    elif score >= 70:
        return 1.5

    elif score >= 60:
        return 1.2

    elif score >= 50:
        return 1.0

    else:
        return 0.8


# ==========================
# 平滑系统
# ==========================

def smooth_signal(
    yesterday,
    today
):

    if yesterday is None:

        return today

    result = (
        YESTERDAY_WEIGHT
        *
        yesterday
        +
        TODAY_WEIGHT
        *
        today
    )

    return round(result)
