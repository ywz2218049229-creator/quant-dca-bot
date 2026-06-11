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


# 纳指100
ndx = yf.Ticker("^NDX")
ndx_data = ndx.history(period="5d")

# 标普500
spx = yf.Ticker("^GSPC")
spx_data = spx.history(period="5d")

# VIX
vix = yf.Ticker("^VIX")
vix_data = vix.history(period="5d")


# 计算涨跌幅
ndx_change = (
    (ndx_data["Close"].iloc[-1] - ndx_data["Close"].iloc[-2])
    / ndx_data["Close"].iloc[-2]
    * 100
)

spx_change = (
    (spx_data["Close"].iloc[-1] - spx_data["Close"].iloc[-2])
    / spx_data["Close"].iloc[-2]
    * 100
)

vix_value = vix_data["Close"].iloc[-1]


message = f"""
📊 美股市场监控

纳斯达克100：{ndx_change:.2f}%
标普500：{spx_change:.2f}%
VIX：{vix_value:.2f}

系统运行正常
"""

send_message(message)

print(message)
