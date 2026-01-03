# 🗄️ Guía de Alembic para Sincronizar Modelos con Supabase

## 📋 **Comandos Esenciales**

### 🚀 **1. Generar Nueva Migración**
```bash
# Generar archivo de migración para cambios en modelos
alembic revision --autogenerate -m "descripción_del_cambio"

# Ejemplo para el sistema de logros:
alembic revision --autogenerate -m "add_achievements_system"
```

### ⬆️ **2. Aplicar Migraciones a Base de Datos**
```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar migración específica
alembic upgrade add_achievements_tables

# Aplicar hasta una versión específica
alembic upgrade d617956ef9ba
```

### ⬇️ **3. Revertir Migraciones**
```bash
# Revertir última migración
alembic downgrade -1

# Revertir a versión específica
alembic downgrade d617956ef9ba

# Revertir todo (¡CUIDADO! Borra todo)
alembic downgrade base
```

### 📊 **4. Ver Estado Actual**
```bash
# Ver estado de migraciones
alembic current

# Ver historial de migraciones
alembic history

# Ver migraciones pendientes
alembic heads
```

---

## 🛠️ **Proceso Completo para uSipipo**

### 📝 **Paso 1: Verificar Configuración**

Asegúrate que tu `alembic.ini` esté configurado correctamente:

```ini
# alembic.ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@host:port/database

# Opciones importantes
[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME

[loggers]
keys = root,sqlalchemy,alembic
level = INFO
handlers = console
qualname =
```

### 🔧 **Paso 2: Configurar Variables de Entorno**

Asegúrate que tu `.env` tenga la URL de base de datos:

```bash
# .env
DATABASE_URL=postgresql://tu_usuario:tu_password@tu_host:5432/tu_database
```

### 🚀 **Paso 3: Aplicar Migración de Logros**

```bash
# 1. Verificar estado actual
alembic current

# 2. Aplicar la migración de logros
alembic upgrade add_achievements_tables

# 3. Verificar que se aplicó correctamente
alembic current
```

### ✅ **Paso 4: Verificar en Supabase**

1. **Abre el panel de Supabase**
2. **Ve a "Database" → "Table Editor"**
3. **Deberías ver las nuevas tablas:**
   - `achievements` (56 logros predefinidos)
   - `user_stats` (estadísticas de usuarios)
   - `user_achievements` (progreso de logros)

---

## 🔍 **Troubleshooting Común**

### ❌ **Error: "Target database is not up to date"**
```bash
# Solución: Forzar actualización a versión específica
alembic stamp head
```

### ❌ **Error: "Can't locate revision identified by 'add_achievements_tables'"**
```bash
# Solución: Verificar que el archivo de migración exista
ls migrations/versions/
# Si no existe, regenerarla:
alembic revision --autogenerate -m "add_achievements_tables"
```

### ❌ **Error: "relation already exists"**
```bash
# Solución: Marcar como aplicada si la tabla ya existe
alembic stamp add_achievements_tables
```

### ❌ **Error de conexión a base de datos**
```bash
# Verificar URL de conexión
echo $DATABASE_URL
# O probar conexión directa
psql $DATABASE_URL
```

---

## 🔄 **Flujo de Trabajo Recomendado**

### 📝 **Desarrollo Local**
```bash
# 1. Hacer cambios en modelos
# 2. Generar migración
alembic revision --autogenerate -m "descripción_cambio"

# 3. Revisar archivo generado
# 4. Aplicar migración
alembic upgrade head

# 5. Probar cambios
```

### 🚀 **Producción**
```bash
# 1. Backup de base de datos
pg_dump $DATABASE_URL > backup.sql

# 2. Aplicar migraciones en producción
alembic upgrade head

# 3. Verificar estado
alembic current
```

---

## 🎯 **Comandos Útiles para uSipipo**

### 📊 **Verificar Sistema de Logros**
```bash
# Ver estado actual
alembic current

# Ver todas las migraciones
alembic history --verbose

# Ver migraciones pendientes
alembic heads
```

### 🔧 **Si algo sale mal**
```bash
# Revertir última migración
alembic downgrade -1

# Reaplicar (útil para debugging)
alembic upgrade head

# Forzar estado (si sabes lo que haces)
alembic stamp head
```

---

## 📋 **Checklist Antes de Aplicar**

### ✅ **Verificar:**
- [ ] URL de base de datos en `.env`
- [ ] Archivo `alembic.ini` configurado
- [ ] Models importados correctamente en `versions/env.py`
- [ ] Backup de base de datos (producción)

### 🚀 **Ejecutar:**
```bash
# Comando final para aplicar sistema de logros
alembic upgrade add_achievements_tables
```

### ✅ **Verificar después:**
- [ ] Tablas creadas en Supabase
- [ ] Datos predefinidos insertados
- [ ] No hay errores en logs
- [ ] Bot funciona con nuevos logros

---

## 🎉 **Listo!**

Una vez que ejecutes `alembic upgrade add_achievements_tables`, tu sistema de logros estará completamente sincronizado con Supabase y listo para usar en el bot de uSipipo. 🚀
