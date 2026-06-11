import os
import requests
import pandas as pd
import yfinance as yf

from datetime import datetime

from config import *

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


def get_fear_greed():

    try:

        url = "https://api.alternative.me/fng/"

        data = requests.get(url, timeout=10).json()

        value = int(data["data"][0]["value"])

        label = data["data"][0]["value_classification"]

        return value, label

    except:

        return None, "Unavailable"


# ======================
# 市场数据
# ======================

ndx = yf.Ticker("^NDX")
spx = yf.Ticker("^GSPC")
vix = yf.Ticker("^VIX")

ndx_data = ndx.history(period="max")
spx_data = spx.history(period="5d")
vix_data = vix.history(period="5d")

# ======================
# 涨跌幅
# ======================

ndx_change = (
    (ndx_data["Close"].iloc[-1] -
     ndx_data["Close"].iloc[-2])
    /
    ndx_data["Close"].iloc[-2]
) * 100

spx_change = (
    (spx_data["Close"].iloc[-1] -
     spx_data["Close"].iloc[-2])
    /
    spx_data["Close"].iloc[-2]
) * 100

vix_value = float(vix_data["Close"].iloc[-1])

# ======================
# ATH回撤
# ======================

ndx_now = float(ndx_data["Close"].iloc[-1])

ath = float(ndx_data["Close"].max())

drawdown = (
    (ndx_now - ath)
    / ath
) * 100

# ======================
# RSI
# ======================

delta = ndx_data["Close"].diff()

gain = delta.where(delta > 0, 0)

loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()

avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

rsi = 100 - (100 / (1 + rs))

rsi_value = float(rsi.iloc[-1])

# ======================
# Fear & Greed
# ======================

fg_value, fg_label = get_fear_greed()

# ======================
# 评分系统
# ======================

score = 5

if drawdown <= -20:
    score += 4
elif drawdown <= -15:
    score += 3
elif drawdown <= -10:
    score += 2
elif drawdown <= -5:
    score += 1

if vix_value > 30:
    score += 3
elif vix_value > 25:
    score += 2
elif vix_value > 20:
    score += 1

if rsi_value < 30:
    score += 2
elif rsi_value < 50:
    score += 1

if fg_value is not None:

    if fg_value < 25:
        score += 2

    elif fg_value < 40:
        score += 1

score = min(score, 10)

# ======================
# 周投资金额
# ======================

weekly_budget = MONTHLY_INVEST / 4.345

base_ndx = weekly_budget * TARGET_NDX

base_spx = weekly_budget * TARGET_SPX

cash_extra = 0

if score >= 9:

    ndx_amount = base_ndx * 2

    cash_extra = 2000

elif score == 8:

    ndx_amount = base_ndx * 1.5

elif score == 7:

    ndx_amount = base_ndx * 1.2

else:

    ndx_amount = base_ndx

spx_amount = base_spx

# ======================
# 再平衡
# ======================

total_position = CURRENT_NDX + CURRENT_SPX

ndx_ratio = CURRENT_NDX / total_position * 100

spx_ratio = CURRENT_SPX / total_position * 100

if abs(ndx_ratio - 70) > 5:

    rebalance = "⚠ 建议再平衡"

else:

    rebalance = "✅ 无需调整"

# ======================
# history.csv
# ======================

today = datetime.now().strftime("%Y-%m-%d")

record = {
    "date": today,
    "score": score,
    "vix": round(vix_value, 2),
    "rsi": round(rsi_value, 2),
    "drawdown": round(drawdown, 2),
    "ndx_amount": round(ndx_amount),
    "spx_amount": round(spx_amount)
}

history_file = "history.csv"

if os.path.exists(history_file):

    df = pd.read_csv(history_file)

    if today not in df["date"].astype(str).values:

        df = pd.concat(
            [df, pd.DataFrame([record])],
            ignore_index=True
        )

else:

    df = pd.DataFrame([record])

df.to_csv(history_file, index=False)

# ======================
# invest_log.csv
# ======================

log_file = "invest_log.csv"

if not os.path.exists(log_file):

    pd.DataFrame(
        columns=[
            "date",
            "ndx_actual",
            "spx_actual"
        ]
    ).to_csv(
        log_file,
        index=False
    )

invest_df = pd.read_csv(log_file)

execution_rate = "暂无数据"

if len(invest_df) > 0:

    actual = (
        invest_df["ndx_actual"].sum()
        +
        invest_df["spx_actual"].sum()
    )

    suggested = (
        df["ndx_amount"].sum()
        +
        df["spx_amount"].sum()
    )

    if suggested > 0:

        execution_rate = (
            f"{actual / suggested * 100:.1f}%"
        )

# ======================
# Telegram
# ======================

message = f"""
📊 泡泡投资系统

纳指：{ndx_change:.2f}%
标普：{spx_change:.2f}%

VIX：{vix_value:.2f}
RSI：{rsi_value:.2f}

Fear&Greed：{fg_value}
({fg_label})

ATH回撤：{drawdown:.2f}%

━━━━━━━━━━

综合评分：{score}/10

━━━━━━━━━━

本周执行单

纳指：{ndx_amount:.0f} 元

标普：{spx_amount:.0f} 元

现金仓额外：

{cash_extra:.0f} 元

━━━━━━━━━━

{rebalance}

当前：

纳指 {ndx_ratio:.1f}%
标普 {spx_ratio:.1f}%

目标：

70%
30%

━━━━━━━━━━

执行率：

{execution_rate}
"""

send_message(message)

print(message)
