import requests
import asyncio
import logging
from telegram import Bot
from fastapi import FastAPI
import uvicorn
import threading

logging.basicConfig(level=logging.INFO)

TOKEN = "7898028279:AAF9nIlja0DnvS179zFeKbqqD5ZB_aICP8o"
WALLET = "RMfMCKAUvrQUxBz1fwSEVfkeDQJZAQGzzs"
ZPOOL_API = f"https://www.zpool.ca/api/walletEX?address={WALLET}"
CHAT_ID = "7018107411"  # Thay bằng ID nhóm hoặc cá nhân

bot = Bot(token=TOKEN)

async def send_mining_status():
    while True:
        try:
            response = requests.get(ZPOOL_API).json()

            if not response or "miners" not in response:
                await bot.send_message(CHAT_ID, "❌ Không tìm thấy dữ liệu miner trên Zpool.")
                await asyncio.sleep(10)
                continue

            unsold = response.get("unsold", 0)
            balance = response.get("balance", 0)
            unpaid = response.get("unpaid", 0)
            paid24h = response.get("paid24h", 0)

            miners = response.get("miners", [])
            num_workers = len(miners)
            total_accepted = sum(miner.get("accepted", 0) for miner in miners)
            total_rejected = sum(miner.get("rejected", 0) for miner in miners)

            # Lấy tổng hashrate của MinotaurX
            total_hashrates = response.get("total_hashrates", [])
            minotaurx_hashrate = 0

            if isinstance(total_hashrates, list):
                for entry in total_hashrates:
                    if isinstance(entry, dict) and "minotaurx" in entry:
                        minotaurx_hashrate = entry["minotaurx"]
                        break  # Dừng ngay khi tìm thấy giá trị

            message = (
                f"💎 **Mining Zpool (RVN - MinotaurX)** 💎\n"
                f"💰 Số dư: `{balance:.8f} RVN` | 🕐 Chưa thanh toán: `{unpaid:.8f} RVN`\n"
                f"📌 Chưa bán: `{unsold:.8f} RVN` | 💵 24h: `{paid24h:.8f} RVN`\n"
                f"⚡ Hashrate: `{minotaurx_hashrate:.2f} H/s`\n"
                f"👷‍♂️ Worker: `{num_workers}`"
            )

            await bot.send_message(CHAT_ID, message, parse_mode="Markdown")

        except Exception as e:
            logging.error(f"Lỗi khi lấy dữ liệu mining: {e}")
            await bot.send_message(CHAT_ID, "❌ Lỗi khi lấy dữ liệu từ Zpool.")

        await asyncio.sleep(60)  # Đợi 10 giây trước khi gửi tiếp

async def main():
    logging.info("🚀 Bot Telegram đang chạy! Đang gửi cập nhật mỗi 10s...")
    asyncio.create_task(send_mining_status())  # Chạy bot dưới dạng task

# ========== FASTAPI SERVER ==========
app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "running"}

def run():
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.create_task(main())  # Chạy bot trong event loop
    loop.run_forever()

# Chạy bot trên luồng riêng
threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
