import asyncio
from aiogram import Bot
from config import config


async def delete_webhook():
    bot = Bot(token=config.BOT_TOKEN)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook o'chirildi!")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(delete_webhook())
