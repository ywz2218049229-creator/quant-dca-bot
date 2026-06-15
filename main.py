from market import (
    get_market_data,
    get_fear_greed,
    get_mega_caps,
    get_premarket
)

from scoring import (
    calculate_score
)

from budget import (
    calculate_budget
)

from storage import (
    save_history,
    save_invest,
    get_execution_rate
)

from telegram_bot import (
    send_message
)

from config import *


# ==========================
# 获取市场数据
# ==========================

market = get_market_data()

ndx_change = market["ndx_change"]
spx_change = market["spx_change"]

drawdown = market["drawdown"]

vix = market["vix"]

rsi = market["rsi"]

# Fear & Greed
fg_value, fg_label = get_fear_greed()

# 权重股
mega_caps = get_mega_caps()

# 纳指期货（盘前）
premarket = get_premarket()


# ==========================
# 计算评分
# ==========================

score = calculate_score(

    drawdown=drawdown,

    vix=vix,

    rsi=rsi,

    fear_greed=fg_value,

    mega_caps=mega_caps,

    premarket=premarket
)

# ==========================
# 计算预算
# ==========================

budget = calculate_budget(
    score
)

target_budget = budget[
    "target_budget"
]

invested = budget[
    "invested"
]

remaining_budget = budget[
    "remaining_budget"
]

remaining_days = budget[
    "remaining_days"
]

daily_budget = budget[
    "daily_budget"
]

model_suggestion = budget[
    "model"
]

final_suggestion = budget[
    "final"
]

ndx_amount = budget[
    "ndx"
]

spx_amount = budget[
    "spx"
]

# ==========================
# 保存历史
# ==========================

save_history(

    score=score,

    suggestion=final_suggestion,

    ndx=ndx_amount,

    spx=spx_amount,

    drawdown=drawdown,

    vix=vix,

    rsi=rsi
)

# ==========================
# 自动记录投入
# ==========================

save_invest(

    ndx=ndx_amount,

    spx=spx_amount
)

# ==========================
# 执行率
# ==========================

execution_rate = (
    get_execution_rate()
)
# ==========================
# 市场状态
# ==========================

if score >= 90:

    market_state = "🔥 极佳机会区"

elif score >= 80:

    market_state = "🟢 较好机会区"

elif score >= 70:

    market_state = "🟡 轻度机会区"

elif score >= 60:

    market_state = "⚪ 正常区"

else:

    market_state = "🔴 偏高估区"


# ==========================
# 今日投入合理性
# ==========================

budget_usage = (
    invested
    /
    target_budget
    * 100
)

if budget_usage < 80:

    reason = "✅ 合理"

elif budget_usage < 100:

    reason = "🟡 接近预算"

else:

    reason = "🔴 已超预算"


# ==========================
# Fear & Greed 显示
# ==========================

if fg_value is None:

    fg_text = "Unavailable"

else:

    fg_text = f"{fg_value} ({fg_label})"


# ==========================
# 最终消息
# ==========================

message = f"""
📊 泡泡投资系统 V3.0

市场评分：{score}/100

状态：
{market_state}

━━━━━━━━━━

市场数据

纳指：{ndx_change:.2f}%
标普：{spx_change:.2f}%

ATH回撤：{drawdown:.2f}%

VIX：{vix:.2f}

RSI：{rsi:.2f}

Fear & Greed：
{fg_text}

权重股平均涨跌：
{mega_caps:.2f}%

盘前期货：
{premarket:.2f}%

━━━━━━━━━━

预算系统

目标预算：
{target_budget:.0f} 元

已投入：
{invested:.0f} 元

剩余预算：
{remaining_budget:.0f} 元

剩余交易日：
{remaining_days} 天

理论日预算：
{daily_budget:.0f} 元

━━━━━━━━━━

昨日平滑后建议：

{final_suggestion:.0f} 元

今日模型建议：

{model_suggestion:.0f} 元

━━━━━━━━━━

今日买入建议

纳指：
{ndx_amount:.0f} 元

标普：
{spx_amount:.0f} 元

合计：
{final_suggestion:.0f} 元

━━━━━━━━━━

预算利用率：

{budget_usage:.1f}%

投入合理性：

{reason}

━━━━━━━━━━

执行率：

{execution_rate}
"""


# ==========================
# Telegram 推送
# ==========================

send_message(message)

print(message)
