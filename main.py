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


# 获取数据
ndx = yf.Ticker("^NDX")
spx = yf.Ticker("^GSPC")
vix = yf.Ticker("^VIX")

ndx_data = ndx.history(period="1y")
spx_data = spx.history(period="5d")
vix_data = vix.history(period="5d")

# 当前价格
ndx_now = ndx_data["Close"].iloc[-1]

# 一年内最高点
ndx_high = ndx_data["Close"].max()

# 回撤
drawdown = (ndx_now - ndx_high) / ndx_high * 100

# VIX
vix_value = vix_data["Close"].iloc[-1]

# 昨日涨跌
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


# -------------------
# 机会评分系统
# -------------------

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

score = min(score, 10)

# -------------------
# 定投建议
# -------------------

if score >= 9:
    ndx_advice = "正常定投 +100%"
    spx_advice = "正常定投"
    cash_advice = "启动现金仓"

elif score >= 8:
    ndx_advice = "正常定投 +50%"
    spx_advice = "正常定投"
    cash_advice = "小幅启用现金仓"

elif score >= 7:
    ndx_advice = "正常定投 +20%"
    spx_advice = "正常定投"
    cash_advice = "继续积累现金"

else:
    ndx_advice = "正常定投"
    spx_advice = "正常定投"
    cash_advice = "继续积累现金"


message = f"""
📊 市场机会评分

纳斯达克100：{ndx_change:.2f}%
标普500：{spx_change:.2f}%

VIX：{vix_value:.2f}

纳指回撤：{drawdown:.2f}%

━━━━━━━━━━

机会评分：{score}/10

━━━━━━━━━━

建议：

纳指：
{ndx_advice}

标普：
{spx_advice}

现金仓：
{cash_advice}

━━━━━━━━━━

"""

send_message(message)

print(message)
