import os
import requests
import yfinance as yf
import pandas as pd

# =========================
# 用户参数（按你的情况填写）
# =========================

CURRENT_NDX = 3855      # 纳指持仓
CURRENT_SPX = 1728      # 标普持仓
CASH = 117577           # 现金仓

MONTHLY_INVEST = 1500   # 每月计划投入

TARGET_NDX = 0.70
TARGET_SPX = 0.30

# =========================
# Telegram
# =========================

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


# =========================
# 获取市场数据
# =========================

ndx = yf.Ticker("^NDX")
spx = yf.Ticker("^GSPC")
vix = yf.Ticker("^VIX")

ndx_data = ndx.history(period="1y")
spx_data = spx.history(period="5d")
vix_data = vix.history(period="5d")

# =========================
# 涨跌幅
# =========================

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

# =========================
# 纳指回撤
# =========================

ndx_now = float(ndx_data["Close"].iloc[-1])
ndx_high = float(ndx_data["Close"].max())

drawdown = (
    (ndx_now - ndx_high)
    / ndx_high
) * 100

# =========================
# RSI(14)
# =========================

delta = ndx_data["Close"].diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

rs = avg_gain / avg_loss

rsi = 100 - (100 / (1 + rs))

rsi_value = float(rsi.iloc[-1])

# =========================
# 评分系统
# =========================

score = 5

# 回撤评分
if drawdown <= -20:
    score += 4
elif drawdown <= -15:
    score += 3
elif drawdown <= -10:
    score += 2
elif drawdown <= -5:
    score += 1

# VIX评分
if vix_value > 30:
    score += 3
elif vix_value > 25:
    score += 2
elif vix_value > 20:
    score += 1

# RSI评分
if rsi_value < 30:
    score += 2
elif rsi_value < 50:
    score += 1
elif rsi_value > 70:
    score -= 1

score = max(0, min(score, 10))

# =========================
# 基础投入
# =========================

base_ndx = MONTHLY_INVEST * TARGET_NDX
base_spx = MONTHLY_INVEST * TARGET_SPX

cash_extra = 0

# =========================
# 动态金额建议
# =========================

if score >= 9:

    ndx_amount = base_ndx * 1.5
    spx_amount = base_spx

    cash_extra = 2000

elif score == 8:

    ndx_amount = base_ndx * 1.3
    spx_amount = base_spx

elif score == 7:

    ndx_amount = base_ndx * 1.2
    spx_amount = base_spx

else:

    ndx_amount = base_ndx
    spx_amount = base_spx

# =========================
# 当前仓位
# =========================

total_position = CURRENT_NDX + CURRENT_SPX

ndx_ratio = (
    CURRENT_NDX / total_position
) * 100

spx_ratio = (
    CURRENT_SPX / total_position
) * 100

# =========================
# 状态描述
# =========================

if score >= 9:
    market_state = "🔥 极佳加仓区"

elif score >= 8:
    market_state = "🟢 较好机会区"

elif score >= 7:
    market_state = "🟡 轻度机会区"

else:
    market_state = "⚪ 正常区"

# =========================
# 推送消息
# =========================

message = f"""
📊 泡泡投资系统

纳斯达克100：{ndx_change:.2f}%
标普500：{spx_change:.2f}%

VIX：{vix_value:.2f}
RSI：{rsi_value:.2f}

纳指回撤：{drawdown:.2f}%

━━━━━━━━━━

综合评分：{score}/10

状态：

{market_state}

━━━━━━━━━━

本月建议

纳指：{ndx_amount:.0f} 元

标普：{spx_amount:.0f} 元

现金仓额外投入：

{cash_extra:.0f} 元

━━━━━━━━━━

当前资产

纳指：{CURRENT_NDX:.0f} 元
标普：{CURRENT_SPX:.0f} 元

现金：{CASH:.0f} 元

━━━━━━━━━━

当前配置

纳指：{ndx_ratio:.1f}%
标普：{spx_ratio:.1f}%

目标配置

纳指：70%
标普：30%
"""

send_message(message)

print(message)
