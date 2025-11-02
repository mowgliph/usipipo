#!/usr/bin/env python3
"""
Integration test script for dual tunnel system.
Tests database migration, CRUD operations, and basic functionality.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import AsyncSessionLocal, init_db
from database.crud import users as crud_users
from database.models import User
from utils.helpers import log_error_and_notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_integration")


async def test_database_connection():
    """Test basic database connection."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def test_database_migration():
    """Test database schema initialization."""
    try:
        await init_db(create=True)
        logger.info("✅ Database migration successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        return False


async def test_user_crud():
    """Test basic user CRUD operations."""
    try:
        async with AsyncSessionLocal() as session:
            # Create test user
            test_user = User(
                telegram_id=123456789,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            logger.info(f"✅ User created: {test_user.id}")

            # Read user
            user = await crud_users.get_user_by_telegram_id(session, 123456789)
            if not user:
                raise Exception("User not found after creation")
            logger.info("✅ User read successful")

            # Update user
            user.last_name = "Updated"
            await session.commit()
            await session.refresh(user)
            if user.last_name != "Updated":
                raise Exception("User update failed")
            logger.info("✅ User update successful")

            # Delete user (cleanup)
            await session.delete(user)
            await session.commit()
            logger.info("✅ User delete successful")

        return True
    except Exception as e:
        logger.error(f"❌ User CRUD failed: {e}")
        return False




async def main():
    """Run all integration tests."""
    logger.info("🚀 Starting integration tests for dual tunnel system")

    tests = [
        ("Database Connection", test_database_connection),
        ("Database Migration", test_database_migration),
        ("User CRUD", test_user_crud),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"Running: {test_name}")
        try:
            if await test_func():
                passed += 1
            else:
                logger.error(f"Test failed: {test_name}")
        except Exception as e:
            logger.error(f"Test error in {test_name}: {e}")

    logger.info(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All integration tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed. Check logs above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)