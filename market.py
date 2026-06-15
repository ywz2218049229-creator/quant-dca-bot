import requests
import yfinance as yf
import pandas as pd
from config import MEGA_CAPS


# ==========================
# Fear & Greed
# ==========================

def get_fear_greed():

    try:

        url = "https://api.alternative.me/fng/"

        data = requests.get(
            url,
            timeout=10
        ).json()

        value = int(
            data["data"][0]["value"]
        )

        label = data["data"][0][
            "value_classification"
        ]

        return value, label

    except:

        return None, "Unavailable"


# ==========================
# RSI
# ==========================

def calculate_rsi(close):

    delta = close.diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(
        14
    ).mean()

    avg_loss = loss.rolling(
        14
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (
        100 / (1 + rs)
    )

    return float(
        rsi.iloc[-1]
    )


# ==========================
# 纳指市场数据
# ==========================

def get_market_data():

    ndx = yf.Ticker("^NDX")

    spx = yf.Ticker("^GSPC")

    vix = yf.Ticker("^VIX")

    ndx_data = ndx.history(
        period="max"
    )

    spx_data = spx.history(
        period="5d"
    )

    vix_data = vix.history(
        period="5d"
    )

    ndx_now = float(
        ndx_data["Close"].iloc[-1]
    )

    ath = float(
        ndx_data["Close"].max()
    )

    drawdown = (
        (ndx_now - ath)
        / ath
    ) * 100

    vix_value = float(
        vix_data["Close"].iloc[-1]
    )

    rsi_value = calculate_rsi(
        ndx_data["Close"]
    )

    ndx_change = (
        (
            ndx_data["Close"].iloc[-1]
            -
            ndx_data["Close"].iloc[-2]
        )
        /
        ndx_data["Close"].iloc[-2]
    ) * 100

    spx_change = (
        (
            spx_data["Close"].iloc[-1]
            -
            spx_data["Close"].iloc[-2]
        )
        /
        spx_data["Close"].iloc[-2]
    ) * 100

    return {

        "ndx_change":
            round(
                ndx_change,
                2
            ),

        "spx_change":
            round(
                spx_change,
                2
            ),

        "drawdown":
            round(
                drawdown,
                2
            ),

        "vix":
            round(
                vix_value,
                2
            ),

        "rsi":
            round(
                rsi_value,
                2
            )
    }


# ==========================
# 权重股平均跌幅
# ==========================

def get_mega_caps():

    changes = []

    for ticker in MEGA_CAPS:

        try:

            stock = yf.Ticker(
                ticker
            )

            data = stock.history(
                period="5d"
            )

            change = (
                (
                    data["Close"].iloc[-1]
                    -
                    data["Close"].iloc[-2]
                )
                /
                data["Close"].iloc[-2]
            ) * 100

            changes.append(
                change
            )

        except:

            pass

    if len(changes) == 0:

        return 0

    return round(
        sum(changes)
        /
        len(changes),
        2
    )


# ==========================
# 纳指盘前期货
# ==========================

def get_premarket():

    try:

        future = yf.Ticker(
            "NQ=F"
        )

        data = future.history(
            period="2d",
            interval="1h"
        )

        if len(data) < 2:

            return 0

        premarket = (
            (
                data["Close"].iloc[-1]
                -
                data["Close"].iloc[-2]
            )
            /
            data["Close"].iloc[-2]
        ) * 100

        return round(
            premarket,
            2
        )

    except:

        return 0
