"""
Main entry point - Bot ishga tushirish
"""
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import config
from database import init_db
from middlewares import SubscriptionMiddleware

# Handlers
from handlers import start, registration, services, orders, admin, commands

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
    ]
)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Bot ishga tushganda"""
    try:
        # Database'ni initsializatsiya qilish
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        # Bot ma'lumotlarini olish
        bot_info = await bot.me()
        logger.info(f"Bot started: @{bot_info.username} (ID: {bot_info.id})")
        
        # Adminlarga xabar yuborish
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"✅ Bot ishga tushdi!\n\n"
                    f"🤖 Bot: @{bot_info.username}\n"
                    f"🆔 ID: {bot_info.id}"
                )
            except Exception as e:
                logger.error(f"Error sending startup message to admin {admin_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error in on_startup: {e}")
        raise


async def on_shutdown(bot: Bot):
    """Bot to'xtaganda"""
    try:
        logger.info("Shutting down bot...")
        
        # Adminlarga xabar yuborish
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    "⚠️ Bot to'xtatildi!"
                )
            except Exception as e:
                logger.error(f"Error sending shutdown message to admin {admin_id}: {e}")
        
        logger.info("Bot stopped successfully")
    
    except Exception as e:
        logger.error(f"Error in on_shutdown: {e}")


async def main():
    """Asosiy funksiya"""
    try:
        # Bot va Dispatcher yaratish
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        
        # Middleware'larni qo'shish
        # Subscription middleware faqat private chat uchun
        dp.message.middleware(SubscriptionMiddleware())
        dp.callback_query.middleware(SubscriptionMiddleware())
        
        # Router'larni qo'shish
        dp.include_router(start.router)
        dp.include_router(registration.router)
        dp.include_router(services.router)
        dp.include_router(orders.router)
        dp.include_router(admin.router)
        dp.include_router(commands.router)
        
        # Startup va shutdown handlerlar
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Polling boshlash
        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
