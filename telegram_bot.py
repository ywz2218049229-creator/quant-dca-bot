import os
import requests


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)

CHAT_ID = os.getenv(
    "CHAT_ID"
)


# ==========================
# 发送文本消息
# ==========================

def send_message(text):

    if (
        BOT_TOKEN is None
        or
        CHAT_ID is None
    ):

        print(
            "Telegram secrets missing"
        )

        return

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    try:

        response = requests.post(

            url,

            data={

                "chat_id":
                    CHAT_ID,

                "text":
                    text,

                "parse_mode":
                    "Markdown"
            },

            timeout=20
        )

        if (
            response.status_code
            !=
            200
        ):

            print(
                response.text
            )

    except Exception as e:

        print(
            f"Telegram error: {e}"
        )
