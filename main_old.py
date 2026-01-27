"""
Main Bot File
Bot initialization va run
"""
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database import init_db
from states import DatabaseMiddleware, UserCheckMiddleware, AdminCheckMiddleware
from scheduler import init_scheduler, stop_scheduler
from utils import LogHelper

# Logging o'rnatish
logger = LogHelper.setup_logging()

# Handlers import
from handlers import start, driver_registration, passenger_registration, orders, admin


async def setup_commands(bot: Bot):
    """Bot komandalarini o'rnatish"""
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="menu", description="Menyu"),
        BotCommand(command="admin", description="Admin paneli"),
        BotCommand(command="help", description="Yordam"),
    ]
    
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    logger.info("Bot commands set successfully")


async def main():
    """Main funksiya"""
    
    # Database bilan bog'lanish
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    
    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Middlewares qo'shish
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(UserCheckMiddleware())
    dp.message.middleware(AdminCheckMiddleware())
    
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(UserCheckMiddleware())
    dp.callback_query.middleware(AdminCheckMiddleware())
    
    # Handlers ro'yxatlarini qo'shish
    main_router = Router()
    
    main_router.include_router(start.router)
    main_router.include_router(driver_registration.router)
    main_router.include_router(passenger_registration.router)
    main_router.include_router(orders.router)
    main_router.include_router(admin.router)
    
    dp.include_router(main_router)
    
    # Bot komandalarini o'rnatish
    await setup_commands(bot)
    
    # Schedulerni ishga tushirish
    logger.info("Starting scheduler...")
    await init_scheduler(bot)
    logger.info("Scheduler started")
    
    # Bot-ni long polling-da boshlash
    try:
        logger.info("Bot starting with long polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            skip_updates=True
        )
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        # Cleanup
        stop_scheduler()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    
    # .env file ni load qilish (optional)
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Environment variables loaded from .env")
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env loading")
    
    # Bot-ni boshlash
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
