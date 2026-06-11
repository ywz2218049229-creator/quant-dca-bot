import os
import requests
import yfinance as yf

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


# 数据获取
ndx = yf.Ticker("^NDX")
spx = yf.Ticker("^GSPC")
vix = yf.Ticker("^VIX")

ndx_data = ndx.history(period="5d")
spx_data = spx.history(period="5d")
vix_data = vix.history(period="5d")

# 涨跌幅
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

vix_value = vix_data["Close"].iloc[-1]

# 评分系统
score = 5

# VIX评分
if vix_value < 15:
    score += 2
elif vix_value < 20:
    score += 1
elif vix_value > 30:
    score -= 2

# 纳指评分
if ndx_change > 1:
    score += 1
elif ndx_change < -2:
    score -= 1

# 标普评分
if spx_change > 1:
    score += 1
elif spx_change < -2:
    score -= 1

score = max(0, min(score, 10))

# 投资建议
if score >= 8:
    advice = "🟢 正常定投"
elif score >= 5:
    advice = "🟡 保持观察"
else:
    advice = "🔴 谨慎投入"

message = f"""
📊 每日市场评分

纳斯达克100：{ndx_change:.2f}%
标普500：{spx_change:.2f}%
VIX：{vix_value:.2f}

风险评分：{score}/10

━━━━━━━━━━

建议：

纳指：{advice}
标普：{advice}

━━━━━━━━━━
"""

send_message(message)

print(message)
