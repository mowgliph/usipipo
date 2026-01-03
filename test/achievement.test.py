"""
Tests para el sistema de logros de uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

import pytest
import asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock, patch

from domain.entities.achievement import (
    Achievement, UserAchievement, UserStats, AchievementType, AchievementTier,
    ACHIEVEMENTS_DEFINITIONS, get_achievements_by_type, get_achievement_by_id
)
from application.services.achievement_service import AchievementService
from infrastructure.persistence.supabase.achievement_repository import AchievementRepository, UserStatsRepository
from telegram_bot.messages.achievement_messages import AchievementMessages


class TestAchievementEntities:
    """Tests para las entidades de logros."""
    
    def test_achievement_creation(self):
        """Test de creación de logro."""
        achievement = Achievement(
            id="test_achievement",
            name="Test Achievement",
            description="Test description",
            type=AchievementType.DATA_CONSUMED,
            tier=AchievementTier.BRONZE,
            requirement_value=10,
            reward_stars=5,
            icon="🥉"
        )
        
        assert achievement.id == "test_achievement"
        assert achievement.name == "Test Achievement"
        assert achievement.type == AchievementType.DATA_CONSUMED
        assert achievement.tier == AchievementTier.BRONZE
        assert achievement.requirement_value == 10
        assert achievement.reward_stars == 5
        assert achievement.icon == "🥉"
        assert achievement.is_active is True
    
    def test_user_achievement_progress(self):
        """Test de progreso de logro de usuario."""
        user_achievement = UserAchievement(
            user_id=12345,
            achievement_id="test_achievement",
            current_value=5
        )
        
        # Test actualización sin completar
        completed = user_achievement.update_progress(8)
        assert completed is False
        assert user_achievement.current_value == 8
        assert user_achievement.is_completed is False
        
        # Test actualización completando
        completed = user_achievement.update_progress(12)
        assert completed is True
        assert user_achievement.current_value == 12
        assert user_achievement.is_completed is True
        assert user_achievement.completed_at is not None
    
    def test_user_achievement_reward_claim(self):
        """Test de reclamo de recompensa."""
        user_achievement = UserAchievement(
            user_id=12345,
            achievement_id="test_achievement",
            current_value=10,
            is_completed=True,
            completed_at=datetime.now()
        )
        
        # Test reclamo exitoso
        claimed = user_achievement.claim_reward()
        assert claimed is True
        assert user_achievement.reward_claimed is True
        assert user_achievement.reward_claimed_at is not None
        
        # Test intento de reclamo duplicado
        claimed_again = user_achievement.claim_reward()
        assert claimed_again is False
    
    def test_user_stats_updates(self):
        """Test de actualización de estadísticas de usuario."""
        user_stats = UserStats(user_id=12345)
        
        # Test actualización de datos consumidos
        user_stats.update_data_consumed(5.5)
        assert user_stats.total_data_consumed_gb == 5.5
        
        user_stats.update_data_consumed(2.3)
        assert user_stats.total_data_consumed_gb == 7.8
        
        # Test actualización de actividad diaria
        today = date.today()
        user_stats.update_daily_activity()
        assert user_stats.days_active == 1
        assert user_stats.last_active_date == today
        
        # Test incrementos
        user_stats.increment_referrals()
        assert user_stats.total_referrals == 1
        
        user_stats.add_stars_deposited(100)
        assert user_stats.total_stars_deposited == 100
        
        user_stats.increment_keys_created()
        assert user_stats.total_keys_created == 1
        
        user_stats.increment_games_won()
        assert user_stats.total_games_won == 1
        
        user_stats.add_vip_months(3)
        assert user_stats.vip_months_purchased == 3
    
    def test_achievement_definitions(self):
        """Test de definiciones predefinidas de logros."""
        # Verificar que existan logros de cada tipo
        for achievement_type in AchievementType:
            achievements = get_achievements_by_type(achievement_type)
            assert len(achievements) > 0
            assert all(a.type == achievement_type for a in achievements)
        
        # Test de búsqueda por ID
        test_achievement = ACHIEVEMENTS_DEFINITIONS[0]
        found = get_achievement_by_id(test_achievement.id)
        assert found is not None
        assert found.id == test_achievement.id
        
        # Test de búsqueda no existente
        not_found = get_achievement_by_id("non_existent")
        assert not_found is None


class TestAchievementService:
    """Tests para el servicio de logros."""
    
    @pytest.fixture
    def mock_achievement_repository(self):
        """Mock del repositorio de logros."""
        repo = AsyncMock(spec=AchievementRepository)
        return repo
    
    @pytest.fixture
    def mock_user_stats_repository(self):
        """Mock del repositorio de estadísticas de usuario."""
        repo = AsyncMock(spec=UserStatsRepository)
        return repo
    
    @pytest.fixture
    def achievement_service(self, mock_achievement_repository, mock_user_stats_repository):
        """Instancia del servicio de logros con mocks."""
        return AchievementService(mock_achievement_repository, mock_user_stats_repository)
    
    @pytest.mark.asyncio
    async def test_initialize_user_achievements(self, achievement_service, mock_achievement_repository, mock_user_stats_repository):
        """Test de inicialización de logros para usuario."""
        user_id = 12345
        
        # Mock de logros disponibles
        mock_achievements = [
            Achievement("test1", "Test 1", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 1, 5, "🥉"),
            Achievement("test2", "Test 2", "Desc", AchievementType.DAYS_ACTIVE, AchievementTier.SILVER, 7, 15, "🥈")
        ]
        mock_achievement_repository.get_all_achievements.return_value = mock_achievements
        mock_achievement_repository.get_user_achievement.return_value = None  # No existen
        
        # Mock de estadísticas
        mock_user_stats_repository.get_user_stats.return_value = None  # No existen
        
        # Ejecutar inicialización
        await achievement_service.initialize_user_achievements(user_id)
        
        # Verificaciones
        mock_user_stats_repository.create_user_stats.assert_called_once()
        assert mock_achievement_repository.create_user_achievement.call_count == len(mock_achievements)
    
    @pytest.mark.asyncio
    async def test_update_user_stats_data_consumed(self, achievement_service, mock_achievement_repository, mock_user_stats_repository):
        """Test de actualización de estadísticas de consumo de datos."""
        user_id = 12345
        stats_update = {'data_consumed_gb': 5.5}
        
        # Mock de estadísticas existentes
        mock_user_stats = UserStats(user_id=user_id, total_data_consumed_gb=2.0)
        mock_user_stats_repository.get_user_stats.return_value = mock_user_stats
        
        # Mock de logros del tipo consumo
        mock_achievements = [
            Achievement("data_test", "Data Test", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 10, 5, "🥉")
        ]
        mock_achievement_repository.get_achievements_by_type.return_value = mock_achievements
        
        # Mock de logro de usuario existente
        mock_user_achievement = UserAchievement(user_id=user_id, achievement_id="data_test", current_value=2)
        mock_achievement_repository.get_user_achievement.return_value = mock_user_achievement
        
        # Ejecutar actualización
        await achievement_service.update_user_stats(user_id, stats_update)
        
        # Verificaciones
        mock_user_stats_repository.update_user_stats.assert_called_once()
        assert mock_user_stats.total_data_consumed_gb == 7.5  # 2.0 + 5.5
    
    @pytest.mark.asyncio
    async def test_check_and_update_achievements(self, achievement_service, mock_achievement_repository):
        """Test de verificación y actualización de logros."""
        user_id = 12345
        achievement_type = AchievementType.DATA_CONSUMED
        new_value = 15
        
        # Mock de logros del tipo
        mock_achievement = Achievement("data_test", "Data Test", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 10, 5, "🥉")
        mock_achievements = [mock_achievement]
        mock_achievement_repository.get_achievements_by_type.return_value = mock_achievements
        
        # Mock de logro de usuario existente
        mock_user_achievement = UserAchievement(user_id=user_id, achievement_id="data_test", current_value=5)
        mock_achievement_repository.get_user_achievement.return_value = mock_user_achievement
        
        # Ejecutar verificación
        completed = await achievement_service.check_and_update_achievements(user_id, achievement_type, new_value)
        
        # Verificaciones
        assert len(completed) == 1
        assert completed[0].id == "data_test"
        assert mock_user_achievement.current_value == 15
        assert mock_user_achievement.is_completed is True
        mock_achievement_repository.update_user_achievement.assert_called()
    
    @pytest.mark.asyncio
    async def test_claim_achievement_reward(self, achievement_service, mock_achievement_repository):
        """Test de reclamo de recompensa de logro."""
        user_id = 12345
        achievement_id = "test_achievement"
        
        # Mock de logro completado no reclamado
        mock_user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            is_completed=True,
            reward_claimed=False
        )
        mock_achievement_repository.get_user_achievement.return_value = mock_user_achievement
        
        # Mock de detalles del logro
        mock_achievement = Achievement(achievement_id, "Test", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 10, 5, "🥉")
        mock_achievement_repository.get_achievement_by_id.return_value = mock_achievement
        
        # Ejecutar reclamo
        result = await achievement_service.claim_achievement_reward(user_id, achievement_id)
        
        # Verificaciones
        assert result is True
        assert mock_user_achievement.reward_claimed is True
        mock_achievement_repository.update_user_achievement.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_summary(self, achievement_service, mock_achievement_repository, mock_user_stats_repository):
        """Test de obtención de resumen de usuario."""
        user_id = 12345
        
        # Mock de estadísticas
        mock_user_stats = UserStats(
            user_id=user_id,
            total_data_consumed_gb=25.5,
            days_active=30,
            total_referrals=5,
            total_stars_deposited=100,
            total_keys_created=8,
            total_games_won=12,
            vip_months_purchased=3
        )
        mock_user_stats_repository.get_user_stats.return_value = mock_user_stats
        
        # Mock de logros completados
        mock_completed_achievements = [
            UserAchievement(user_id=user_id, achievement_id="test1", is_completed=True, completed_at=datetime.now()),
            UserAchievement(user_id=user_id, achievement_id="test2", is_completed=True, completed_at=datetime.now())
        ]
        mock_achievement_repository.get_completed_achievements.return_value = mock_completed_achievements
        
        # Mock de logros pendientes
        mock_pending_rewards = [
            UserAchievement(user_id=user_id, achievement_id="test3", is_completed=True, reward_claimed=False)
        ]
        mock_achievement_repository.get_pending_rewards.return_value = mock_pending_rewards
        
        # Mock de logros totales
        mock_achievement_repository.get_all_achievements.return_value = [MagicMock() for _ in range(10)]
        
        # Mock de detalles de logros para cálculo de estrellas
        mock_achievement_repository.get_achievement_by_id.return_value = MagicMock(reward_stars=10)
        
        # Ejecutar obtención de resumen
        summary = await achievement_service.get_user_summary(user_id)
        
        # Verificaciones
        assert summary['completed_achievements'] == 2
        assert summary['total_achievements'] == 10
        assert summary['completion_percentage'] == 20.0
        assert summary['pending_rewards'] == 1
        assert summary['total_reward_stars'] == 20  # 2 logros * 10 estrellas


class TestAchievementMessages:
    """Tests para los mensajes de logros."""
    
    def test_progress_bar_generation(self):
        """Test de generación de barra de progreso."""
        # Test 0%
        bar = AchievementMessages.get_progress_bar(0, 100, 10)
        assert bar == "[░░░░░░░░░░] 0.0%"
        
        # Test 50%
        bar = AchievementMessages.get_progress_bar(50, 100, 10)
        assert bar == "[█████░░░░░] 50.0%"
        
        # Test 100%
        bar = AchievementMessages.get_progress_bar(100, 100, 10)
        assert bar == "[██████████] 100.0%"
        
        # Test con límite diferente
        bar = AchievementMessages.get_progress_bar(25, 50, 20)
        assert bar == "[████████████████] 50.0%"
    
    def test_format_achievement_list(self):
        """Test de formateo de lista de logros."""
        achievements = [
            {'name': 'Test 1', 'icon': '🥉', 'is_completed': True},
            {'name': 'Test 2', 'icon': '🥈', 'is_completed': False}
        ]
        
        formatted = AchievementMessages.format_achievement_list(achievements)
        
        assert "🥉 **Test 1** - ✅ Completado" in formatted
        assert "🥈 **Test 2** - ⏳ En progreso" in formatted
    
    def test_format_leaderboard_entry(self):
        """Test de formateo de entrada de ranking."""
        entry = {'user_id': 12345, 'value': 100}
        
        # Test primer lugar
        formatted = AchievementMessages.format_leaderboard_entry(entry, 0)
        assert "🥇 Usuario 12345: 100" in formatted
        
        # Test segundo lugar
        formatted = AchievementMessages.format_leaderboard_entry(entry, 1)
        assert "🥈 Usuario 12345: 100" in formatted
        
        # Test tercer lugar
        formatted = AchievementMessages.format_leaderboard_entry(entry, 2)
        assert "🥉 Usuario 12345: 100" in formatted
        
        # Test otros lugares
        formatted = AchievementMessages.format_leaderboard_entry(entry, 5)
        assert "#6 Usuario 12345: 100" in formatted


class TestAchievementIntegration:
    """Tests de integración para el sistema de logros."""
    
    @pytest.mark.asyncio
    async def test_full_achievement_flow(self):
        """Test del flujo completo de un logro."""
        # Este test simula el flujo completo desde creación hasta reclamo
        
        # 1. Crear servicio con repositorios mock
        mock_achievement_repo = AsyncMock(spec=AchievementRepository)
        mock_user_stats_repo = AsyncMock(spec=UserStatsRepository)
        service = AchievementService(mock_achievement_repo, mock_user_stats_repo)
        
        user_id = 12345
        
        # 2. Inicializar logros para nuevo usuario
        mock_achievement_repo.get_all_achievements.return_value = [
            Achievement("test_1", "Test 1", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 10, 5, "🥉")
        ]
        mock_achievement_repo.get_user_achievement.return_value = None
        mock_user_stats_repo.get_user_stats.return_value = None
        
        await service.initialize_user_achievements(user_id)
        
        # 3. Simular actividad que actualiza estadísticas
        mock_user_stats = UserStats(user_id=user_id)
        mock_user_stats_repo.get_user_stats.return_value = mock_user_stats
        mock_achievement_repo.get_achievements_by_type.return_value = [
            Achievement("test_1", "Test 1", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 10, 5, "🥉")
        ]
        
        mock_user_achievement = UserAchievement(user_id=user_id, achievement_id="test_1", current_value=0)
        mock_achievement_repo.get_user_achievement.return_value = mock_user_achievement
        
        # 4. Actualizar estadísticas que deberían completar el logro
        completed = await service.update_user_stats(user_id, {'data_consumed_gb': 15})
        
        # 5. Verificar que el logro se completó
        assert mock_user_achievement.is_completed is True
        assert mock_user_achievement.current_value == 15
        
        # 6. Reclamar recompensa
        mock_achievement_repo.get_achievement_by_id.return_value = Achievement("test_1", "Test 1", "Desc", AchievementType.DATA_CONSUMED, AchievementTier.BRONZE, 10, 5, "🥉")
        
        reward_claimed = await service.claim_achievement_reward(user_id, "test_1")
        
        # 7. Verificar que la recompensa fue reclamada
        assert reward_claimed is True
        assert mock_user_achievement.reward_claimed is True


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
