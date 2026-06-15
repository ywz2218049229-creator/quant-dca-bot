import os
import pandas as pd
from datetime import datetime


# ==========================
# 保存每日记录
# ==========================

def save_history(
    score,
    suggestion,
    ndx,
    spx,
    drawdown,
    vix,
    rsi
):

    file = "history.csv"

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    record = {
        "date": today,
        "score": score,
        "suggestion": suggestion,
        "ndx": ndx,
        "spx": spx,
        "drawdown": drawdown,
        "vix": vix,
        "rsi": rsi
    }

    new_df = pd.DataFrame(
        [record]
    )

    if os.path.exists(file):

        df = pd.read_csv(file)

        # 防止同一天重复写入
        if (
            today
            in
            df["date"]
            .astype(str)
            .values
        ):

            return

        df = pd.concat(
            [df, new_df],
            ignore_index=True
        )

    else:

        df = new_df

    df.to_csv(
        file,
        index=False
    )


# ==========================
# 自动记录投入
# ==========================

def save_invest(
    ndx,
    spx
):

    file = "invest_log.csv"

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    record = {
        "date": today,
        "actual_ndx": ndx,
        "actual_spx": spx
    }

    new_df = pd.DataFrame(
        [record]
    )

    if os.path.exists(file):

        df = pd.read_csv(file)

        if (
            today
            in
            df["date"]
            .astype(str)
            .values
        ):

            return

        df = pd.concat(
            [df, new_df],
            ignore_index=True
        )

    else:

        df = new_df

    df.to_csv(
        file,
        index=False
    )


# ==========================
# 累计建议投入
# ==========================

def get_total_suggestion():

    file = "history.csv"

    if not os.path.exists(file):

        return 0

    df = pd.read_csv(file)

    if len(df) == 0:

        return 0

    return float(
        df["suggestion"].sum()
    )


# ==========================
# 执行率
# ==========================

def get_execution_rate():

    history = "history.csv"

    invest = "invest_log.csv"

    if (
        not os.path.exists(history)
        or
        not os.path.exists(invest)
    ):

        return "暂无数据"

    h = pd.read_csv(history)

    i = pd.read_csv(invest)

    suggested = (
        h["suggestion"].sum()
    )

    actual = (
        i["actual_ndx"].sum()
        +
        i["actual_spx"].sum()
    )

    if suggested == 0:

        return "暂无数据"

    rate = (
        actual
        /
        suggested
        *
        100
    )

    return f"{rate:.1f}%"
