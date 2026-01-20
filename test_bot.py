#!/usr/bin/env python3
"""
Test Script - Bot funksiyalarini tekshirish
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from datetime import datetime

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def test_imports():
    """Test barcha modullarni import qilish"""
    print(f"{Colors.BLUE}Testing imports...{Colors.END}")
    
    try:
        import config
        print(f"{Colors.GREEN}✓ config.py{Colors.END}")
    except ImportError as e:
        print(f"{Colors.RED}✗ config.py: {e}{Colors.END}")
        return False
    
    try:
        import database
        print(f"{Colors.GREEN}✓ database.py{Colors.END}")
    except ImportError as e:
        print(f"{Colors.RED}✗ database.py: {e}{Colors.END}")
        return False
    
    try:
        import crud
        print(f"{Colors.GREEN}✓ crud.py{Colors.END}")
    except ImportError as e:
        print(f"{Colors.RED}✗ crud.py: {e}{Colors.END}")
        return False
    
    try:
        import states
        print(f"{Colors.GREEN}✓ states.py{Colors.END}")
    except ImportError as e:
        print(f"{Colors.RED}✗ states.py: {e}{Colors.END}")
        return False
    
    try:
        import keyboards
        print(f"{Colors.GREEN}✓ keyboards.py{Colors.END}")
    except ImportError as e:
        print(f"{Colors.RED}✗ keyboards.py: {e}{Colors.END}")
        return False
    
    try:
        import utils
        print(f"{Colors.GREEN}✓ utils.py{Colors.END}")
    except ImportError as e:
        print(f"{Colors.RED}✗ utils.py: {e}{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}All imports successful!{Colors.END}\n")
    return True


def test_config():
    """Test konfiguratsiyani tekshirish"""
    print(f"{Colors.BLUE}Testing configuration...{Colors.END}")
    
    from config import config
    
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"{Colors.RED}✗ BOT_TOKEN o'rnatilmagan{Colors.END}")
        return False
    else:
        print(f"{Colors.GREEN}✓ BOT_TOKEN o'rnatilgan{Colors.END}")
    
    if not config.ADMIN_IDS:
        print(f"{Colors.YELLOW}⚠ ADMIN_IDS bo'sh{Colors.END}")
    else:
        print(f"{Colors.GREEN}✓ ADMIN_IDS: {len(config.ADMIN_IDS)} ta{Colors.END}")
    
    print(f"{Colors.GREEN}✓ Channel ID: {config.CHANNEL_ID}{Colors.END}")
    print(f"{Colors.GREEN}✓ Drivers Group: {config.DRIVERS_GROUP_ID}{Colors.END}")
    print(f"{Colors.GREEN}✓ Database: {config.DATABASE_URL[:30]}...{Colors.END}\n")
    
    return True


def test_database():
    """Test database connection"""
    print(f"{Colors.BLUE}Testing database...{Colors.END}")
    
    try:
        from database import init_db, SessionLocal, User
        
        # Initialize database
        init_db()
        print(f"{Colors.GREEN}✓ Database initialized{Colors.END}")
        
        # Test connection
        db = SessionLocal()
        try:
            # Try to query users table
            count = db.query(User).count()
            print(f"{Colors.GREEN}✓ Database connection successful{Colors.END}")
            print(f"{Colors.GREEN}✓ Users in database: {count}{Colors.END}")
        finally:
            db.close()
        
    except Exception as e:
        print(f"{Colors.RED}✗ Database error: {e}{Colors.END}")
        return False
    
    print()
    return True


def test_crud():
    """Test CRUD operatsiyalari"""
    print(f"{Colors.BLUE}Testing CRUD operations...{Colors.END}")
    
    try:
        from database import SessionLocal
        from crud import create_user, get_user_by_telegram_id, update_user
        
        db = SessionLocal()
        try:
            # Test user creation (with test ID)
            test_telegram_id = 999999999
            
            # Check if exists
            existing = get_user_by_telegram_id(db, test_telegram_id)
            if existing:
                print(f"{Colors.YELLOW}⚠ Test user already exists{Colors.END}")
            else:
                # Create test user
                user = create_user(
                    db=db,
                    telegram_id=test_telegram_id,
                    first_name="Test",
                    last_name="User",
                    role="passenger"
                )
                print(f"{Colors.GREEN}✓ User created: {user.user_id}{Colors.END}")
                
                # Update user
                update_user(db, user.user_id, phone_number="+998901234567")
                print(f"{Colors.GREEN}✓ User updated{Colors.END}")
                
                # Cleanup
                db.delete(user)
                db.commit()
                print(f"{Colors.GREEN}✓ Test user cleaned up{Colors.END}")
        
        finally:
            db.close()
            
    except Exception as e:
        print(f"{Colors.RED}✗ CRUD error: {e}{Colors.END}")
        return False
    
    print()
    return True


def test_bot_token():
    """Test bot token"""
    print(f"{Colors.BLUE}Testing bot token...{Colors.END}")
    
    try:
        from aiogram import Bot
        from config import config
        
        async def check_token():
            bot = Bot(token=config.BOT_TOKEN)
            try:
                me = await bot.get_me()
                print(f"{Colors.GREEN}✓ Bot connected: @{me.username}{Colors.END}")
                return True
            except Exception as e:
                print(f"{Colors.RED}✗ Bot token error: {e}{Colors.END}")
                return False
            finally:
                await bot.session.close()
        
        result = asyncio.run(check_token())
        print()
        return result
        
    except Exception as e:
        print(f"{Colors.RED}✗ Bot error: {e}{Colors.END}")
        print()
        return False


def main():
    """Main test function"""
    print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}Xizmatlar Bot - Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("CRUD Operations", test_crud),
        ("Bot Token", test_bot_token),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"{Colors.RED}✗ {name} crashed: {e}{Colors.END}\n")
            results.append((name, False))
    
    # Summary
    print(f"{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{name:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All tests passed! Bot is ready to launch.{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}✗ Some tests failed. Please fix before launching.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
