import asyncio
import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import config
from database import init_db
from middlewares import SubscriptionMiddleware
from scheduler import start_scheduler
from handlers import start, registration, services, orders,admin
from middlewares import BanCheckMiddleware


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
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("✅ Database initialized successfully")
        
        logger.info("Checking old orders...")
        from scheduler.startup_checks import check_old_orders_on_startup
        await check_old_orders_on_startup(bot)
        logger.info("✅ Old orders checked successfully")
        
        logger.info("Starting scheduler...")
        start_scheduler(bot)
        logger.info("✅ Scheduler started successfully")
        
        logger.info("Starting health check...")
        from scheduler.startup_checks import health_check_loop
        import asyncio
        asyncio.create_task(health_check_loop(bot), name="health_check_task")
        logger.info("✅ Health check started successfully")
        
        bot_info = await bot.me()
        logger.info(f"✅ Bot started: @{bot_info.username} (ID: {bot_info.id})")
        
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"✅ <b>Bot ishga tushdi!</b>\n\n"
                    f"🤖 Bot: @{bot_info.username}\n"
                    f"🆔 ID: {bot_info.id}\n\n"
                    f"📢 Kanal: {config.CHANNEL_ID}\n"
                    f"🚖 Taxi guruhi: {config.GROUP3}\n"
                    f"🥖 Non guruhi: {config.GROUP4}\n"
                    f"🌾 Yem guruhi: {config.GROUP5}"
                )
            except Exception as e:
                logger.error(f"Error sending startup message to admin {admin_id}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error in on_startup: {e}")
        raise


async def on_shutdown(bot: Bot):
    try:
        logger.info("Shutting down bot...")
        
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    "⚠️ Bot to'xtatildi!"
                )
            except Exception as e:
                logger.error(f"Error sending shutdown message to admin {admin_id}: {e}")
        
        logger.info("✅ Bot stopped successfully")
    
    except Exception as e:
        logger.error(f"❌ Error in on_shutdown: {e}")


async def main():
    try:
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        
        dp.message.middleware(SubscriptionMiddleware())
        dp.callback_query.middleware(SubscriptionMiddleware())
        
        dp.message.middleware(BanCheckMiddleware())
        dp.callback_query.middleware(BanCheckMiddleware())

        dp.include_router(start.router)
        dp.include_router(registration.router)
        dp.include_router(services.router)
        dp.include_router(orders.router)
        dp.include_router(admin.router)
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

