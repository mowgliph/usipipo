# 🗄️ GUÍA DE MIGRACIÓN DE BASE DE DATOS

## Paso a Paso para Actualizar la BD

### 1. Crear Migración de Alembic

```bash
# Navegar a la raíz del proyecto
cd d:\JELVYS\usipipo

# Crear nueva migración
alembic revision --autogenerate -m "add_user_roles_and_premium_features"
```

### 2. Contenido esperado de la migración

El archivo generado en `migrations/versions/` debería contener algo similar a:

```python
"""add user roles and premium features."""
from alembic import op
import sqlalchemy as sa

revision = '...'
down_revision = '...'
branch_labels = None
depends_on = None

def upgrade():
    # Actualizar columna status para incluir nuevo valor
    op.alter_column('users', 'status',
        existing_type=sa.Enum('active', 'suspended', 'free_trial'),
        type_=sa.Enum('active', 'suspended', 'blocked', 'free_trial'),
        existing_nullable=False,
        existing_server_default=sa.text("'active'")
    )
    
    # Agregar columna role
    op.add_column('users', sa.Column('role', sa.String(50), nullable=False, server_default='user'))
    
    # Agregar fechas de expiración para roles premium
    op.add_column('users', sa.Column('task_manager_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('announcer_expires_at', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    op.drop_column('users', 'announcer_expires_at')
    op.drop_column('users', 'task_manager_expires_at')
    op.drop_column('users', 'role')
    
    op.alter_column('users', 'status',
        existing_type=sa.Enum('active', 'suspended', 'blocked', 'free_trial'),
        type_=sa.Enum('active', 'suspended', 'free_trial'),
        existing_nullable=False,
        existing_server_default=sa.text("'active'")
    )
```

### 3. Ejecutar la Migración

```bash
# Aplicar migración
alembic upgrade head

# Verificar que se aplicó correctamente
alembic current
```

### 4. SQL Directo (Alternativa)

Si prefieres ejecutar SQL directamente (NO RECOMENDADO):

```sql
-- 1. Actualizar enum de status
ALTER TABLE users MODIFY COLUMN status ENUM('active', 'suspended', 'blocked', 'free_trial') DEFAULT 'active';

-- 2. Agregar columna role
ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user' AFTER status;

-- 3. Agregar fechas de expiración
ALTER TABLE users ADD COLUMN task_manager_expires_at TIMESTAMP NULL AFTER role;
ALTER TABLE users ADD COLUMN announcer_expires_at TIMESTAMP NULL AFTER task_manager_expires_at;

-- 4. Crear índices para mejor rendimiento
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
```

### 5. Verificación Post-Migración

```bash
# Conectar a BD y verificar
mysql -u [usuario] -p [base_de_datos]

# En la consola MySQL:
DESCRIBE users;

# Debería mostrar las nuevas columnas:
# +-----------------------------+----------------------------+------+-----+---------+-------+
# | Field                       | Type                       | Null | Key | Default | Extra |
# +-----------------------------+----------------------------+------+-----+---------+-------+
# | ...                         | ...                        | ... | ... | ...     | ...   |
# | status                      | enum('active',...)         | NO  |     | active  |       |
# | role                        | varchar(50)                | NO  |     | user    |       |
# | task_manager_expires_at     | timestamp                  | YES |     | NULL    |       |
# | announcer_expires_at        | timestamp                  | YES |     | NULL    |       |
# +-----------------------------+----------------------------+------+-----+---------+-------+
```

---

## Modelos SQLAlchemy Esperados

### Actualizar orm/models.py

Si el proyecto usa SQLAlchemy ORM, actualizar el modelo User:

```python
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    # ... campos existentes ...
    
    status = Column(
        Enum('active', 'suspended', 'blocked', 'free_trial'),
        default='active',
        nullable=False
    )
    
    role = Column(
        String(50),
        default='user',
        nullable=False,
        index=True
    )
    
    task_manager_expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    announcer_expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Métodos auxiliares
    def is_task_manager_active(self):
        from datetime import datetime, timezone
        if self.role != 'task_manager' or not self.task_manager_expires_at:
            return False
        return datetime.now(timezone.utc) < self.task_manager_expires_at
    
    def is_announcer_active(self):
        from datetime import datetime, timezone
        if self.role != 'announcer' or not self.announcer_expires_at:
            return False
        return datetime.now(timezone.utc) < self.announcer_expires_at
```

---

## Rollback (Deshacer Cambios)

Si algo sale mal:

```bash
# Ver historial de migraciones
alembic history

# Retroceder a la versión anterior
alembic downgrade -1

# O retroceder a una versión específica
alembic downgrade [hash_anterior]
```

---

## Pruebas Post-Migración

### 1. Probar en Python

```python
from infrastructure.persistence.database import SessionLocal
from domain.entities.user import User, UserStatus, UserRole
from datetime import datetime, timedelta, timezone

# Crear sesión
session = SessionLocal()

# Crear usuario de prueba
new_user = User(
    telegram_id=123456789,
    username="test_user",
    full_name="Test User",
    status=UserStatus.ACTIVE,
    role=UserRole.TASK_MANAGER,
    task_manager_expires_at=datetime.now(timezone.utc) + timedelta(days=30)
)

session.add(new_user)
session.commit()

print(f"✅ Usuario creado: {new_user.telegram_id}")
print(f"   Rol: {new_user.role}")
print(f"   Estado: {new_user.status}")

# Probar cambio de estado
new_user.status = UserStatus.BLOCKED
session.commit()
print(f"✅ Estado actualizado a: {new_user.status}")

session.close()
```

### 2. Probar en Bot

```python
# En el handler de admin
from application.services.admin_service import AdminService

admin_service = get_admin_service()

# Obtener usuario
user_info = await admin_service.get_user_by_id(123456789)
print(f"Usuario: {user_info}")

# Cambiar estado
result = await admin_service.block_user(123456789)
print(f"Resultado: {result.message}")

# Cambiar rol
result = await admin_service.assign_role_to_user(
    123456789,
    'task_manager',
    duration_days=30
)
print(f"Resultado: {result.message}")
```

---

## Checklist Pre-Migración

- [ ] Backup de base de datos realizado
- [ ] Archivo de migración generado
- [ ] Cambios revisados en el archivo de migración
- [ ] Base de datos en parada (NO hay usuarios conectados)
- [ ] Alembic actualizado (`pip install --upgrade alembic`)
- [ ] Test de rollback preparado

---

## Checklist Post-Migración

- [ ] Migración aplicada exitosamente
- [ ] Columnas nuevas verificadas en BD
- [ ] Índices creados correctamente
- [ ] Datos existentes intactos
- [ ] Application iniciada sin errores
- [ ] Admin panel funciona correctamente
- [ ] Shop cargó sin errores
- [ ] Usuarios listados correctamente

---

## Troubleshooting

### Error: "Alembic version table doesn't exist"
```bash
# Inicializar alembic
alembic stamp head
```

### Error: "Column already exists"
```bash
# Rollback y verificar
alembic downgrade -1

# Limpiar y recrear
# (Requiere acceso directo a BD)
```

### Error: "Enum value not recognized"
```bash
# Asegurarse que el enum está actualizado en BD
# Verificar con:
SHOW COLUMNS FROM users WHERE Field='status';
```

---

## Scripts de Referencia

### Script de Backup

```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mysqldump -u [usuario] -p [base_de_datos] > backup_$TIMESTAMP.sql
echo "Backup realizado: backup_$TIMESTAMP.sql"
```

### Script de Restore

```bash
#!/bin/bash
# restore.sh
mysql -u [usuario] -p [base_de_datos] < $1
echo "Base de datos restaurada"
```

---

**Última actualización**: Enero 2026
**Versión**: 1.0.0
