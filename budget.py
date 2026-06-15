import os
import pandas as pd
import pandas_market_calendars as mcal

from datetime import datetime

from config import *
from scoring import (
    score_to_multiplier,
    smooth_signal
)


# ==========================
# 美股剩余交易日
# ==========================

def get_remaining_trading_days():

    nyse = mcal.get_calendar(
        "NYSE"
    )

    today = datetime.now()

    start = today.strftime(
        "%Y-%m-%d"
    )

    schedule = nyse.schedule(
        start_date=start,
        end_date=END_DATE
    )

    return len(schedule)


# ==========================
# 读取历史建议
# ==========================

def get_yesterday_suggestion():

    file = "history.csv"

    if not os.path.exists(file):

        return None

    df = pd.read_csv(file)

    if len(df) == 0:

        return None

    try:

        return float(
            df.iloc[-1][
                "suggestion"
            ]
        )

    except:

        return None


# ==========================
# 已投入金额
# ==========================

def get_total_invested():

    file = "invest_log.csv"

    if not os.path.exists(file):

        return 0

    df = pd.read_csv(file)

    if len(df) == 0:

        return 0

    total = (
        df[
            "actual_ndx"
        ].sum()
        +
        df[
            "actual_spx"
        ].sum()
    )

    return float(total)


# ==========================
# 动态预算目标
# ==========================

def choose_budget(score):

    if score >= 85:

        return MAX_BUDGET

    elif score >= 65:

        return TARGET_BUDGET

    else:

        return MIN_BUDGET


# ==========================
# 计算今日建议
# ==========================

def calculate_budget(score):

    target_budget = choose_budget(
        score
    )

    invested = get_total_invested()

    remaining_budget = max(
        target_budget
        -
        invested,
        0
    )

    remaining_days = max(
        get_remaining_trading_days(),
        1
    )

    daily_budget = (
        remaining_budget
        /
        remaining_days
    )

    multiplier = (
        score_to_multiplier(
            score
        )
    )

    model_suggestion = (
        daily_budget
        *
        multiplier
    )

    yesterday = (
        get_yesterday_suggestion()
    )

    final_suggestion = (
        smooth_signal(
            yesterday,
            model_suggestion
        )
    )

    ndx_amount = round(
        final_suggestion
        *
        TARGET_NDX
    )

    spx_amount = round(
        final_suggestion
        *
        TARGET_SPX
    )

    return {

        "target_budget":
            target_budget,

        "invested":
            round(
                invested,
                2
            ),

        "remaining_budget":
            round(
                remaining_budget,
                2
            ),

        "remaining_days":
            remaining_days,

        "daily_budget":
            round(
                daily_budget,
                2
            ),

        "model":
            round(
                model_suggestion
            ),

        "final":
            round(
                final_suggestion
            ),

        "ndx":
            ndx_amount,

        "spx":
            spx_amount
    }
