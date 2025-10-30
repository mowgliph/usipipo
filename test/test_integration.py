#!/usr/bin/env python3
"""
Integration test script for tunnel domain system.
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
from database.crud import tunnel_domains as crud_tunnel_domains
from database.models import User, TunnelDomain
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


async def test_tunnel_domain_crud():
    """Test tunnel domain CRUD operations."""
    try:
        async with AsyncSessionLocal() as session:
            # Create test user first
            test_user = User(
                telegram_id=987654321,
                username="tunnel_test_user",
                first_name="Tunnel",
                last_name="Test"
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            # Create tunnel domain
            domain = await crud_tunnel_domains.create_tunnel_domain(
                session=session,
                user_id=str(test_user.id),
                domain_name="test.example.com",
                commit=True
            )
            logger.info(f"✅ Tunnel domain created: {domain.id}")

            # Read domain by ID
            domain_read = await crud_tunnel_domains.get_tunnel_domain_by_id(session, str(domain.id))
            if not domain_read:
                raise Exception("Domain not found by ID")
            logger.info("✅ Tunnel domain read by ID successful")

            # Read domain by name
            domain_by_name = await crud_tunnel_domains.get_tunnel_domain_by_name(session, "test.example.com")
            if not domain_by_name:
                raise Exception("Domain not found by name")
            logger.info("✅ Tunnel domain read by name successful")

            # Update domain
            updated_domain = await crud_tunnel_domains.update_tunnel_domain(
                session=session,
                domain_id=str(domain.id),
                domain_name="updated.example.com",
                commit=True
            )
            if not updated_domain or updated_domain.domain_name != "updated.example.com":
                raise Exception("Domain update failed")
            logger.info("✅ Tunnel domain update successful")

            # List domains for user
            domains = await crud_tunnel_domains.get_tunnel_domains_for_user(session, str(test_user.id))
            if len(domains) != 1:
                raise Exception(f"Expected 1 domain, got {len(domains)}")
            logger.info("✅ Tunnel domain list for user successful")

            # Delete domain
            deleted = await crud_tunnel_domains.delete_tunnel_domain(session, str(domain.id), commit=True)
            if not deleted:
                raise Exception("Domain deletion failed")
            logger.info("✅ Tunnel domain delete successful")

            # Cleanup user
            await session.delete(test_user)
            await session.commit()

        return True
    except Exception as e:
        logger.error(f"❌ Tunnel domain CRUD failed: {e}")
        return False


async def test_tunnel_domain_validation():
    """Test tunnel domain validation logic."""
    try:
        async with AsyncSessionLocal() as session:
            # Create test user
            test_user = User(
                telegram_id=111111111,
                username="validation_test_user",
                first_name="Validation",
                last_name="Test"
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            # Test duplicate domain creation
            domain1 = await crud_tunnel_domains.create_tunnel_domain(
                session=session,
                user_id=str(test_user.id),
                domain_name="duplicate.example.com",
                commit=True
            )

            try:
                domain2 = await crud_tunnel_domains.create_tunnel_domain(
                    session=session,
                    user_id=str(test_user.id),
                    domain_name="duplicate.example.com",
                    commit=True
                )
                raise Exception("Duplicate domain creation should have failed")
            except ValueError as e:
                if "domain_already_exists" not in str(e):
                    raise Exception(f"Unexpected error: {e}")
                logger.info("✅ Duplicate domain validation successful")

            # Cleanup
            await crud_tunnel_domains.delete_tunnel_domain(session, str(domain1.id), commit=True)
            await session.delete(test_user)
            await session.commit()

        return True
    except Exception as e:
        logger.error(f"❌ Tunnel domain validation failed: {e}")
        return False


async def test_tunnel_domain_relationships():
    """Test tunnel domain relationships with VPN configs."""
    try:
        async with AsyncSessionLocal() as session:
            # Create test user
            test_user = User(
                telegram_id=222222222,
                username="relationship_test_user",
                first_name="Relationship",
                last_name="Test"
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            # Create VPN config
            from database.models import VPNConfig
            vpn_config = VPNConfig(
                user_id=str(test_user.id),
                vpn_type="wireguard",
                config_name="Test VPN",
                status="active"
            )
            session.add(vpn_config)
            await session.commit()
            await session.refresh(vpn_config)

            # Create domain with VPN config
            domain = await crud_tunnel_domains.create_tunnel_domain(
                session=session,
                user_id=str(test_user.id),
                domain_name="vpn.example.com",
                vpn_config_id=str(vpn_config.id),
                commit=True
            )

            # Test assignment
            assigned = await crud_tunnel_domains.assign_domain_to_vpn_config(
                session=session,
                domain_id=str(domain.id),
                vpn_config_id=str(vpn_config.id),
                commit=True
            )
            if not assigned:
                raise Exception("Domain assignment failed")
            logger.info("✅ Domain to VPN assignment successful")

            # Test unassignment
            unassigned = await crud_tunnel_domains.unassign_domain_from_vpn_config(
                session=session,
                domain_id=str(domain.id),
                commit=True
            )
            if not unassigned or unassigned.vpn_config_id is not None:
                raise Exception("Domain unassignment failed")
            logger.info("✅ Domain from VPN unassignment successful")

            # Cleanup
            await crud_tunnel_domains.delete_tunnel_domain(session, str(domain.id), commit=True)
            await session.delete(vpn_config)
            await session.delete(test_user)
            await session.commit()

        return True
    except Exception as e:
        logger.error(f"❌ Tunnel domain relationships failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    logger.info("🚀 Starting integration tests for tunnel domain system")

    tests = [
        ("Database Connection", test_database_connection),
        ("Database Migration", test_database_migration),
        ("User CRUD", test_user_crud),
        ("Tunnel Domain CRUD", test_tunnel_domain_crud),
        ("Tunnel Domain Validation", test_tunnel_domain_validation),
        ("Tunnel Domain Relationships", test_tunnel_domain_relationships),
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