"""
Job de Backup de Base de Datos.

Este job se ejecuta según la configuración:
- Backup completo: Semanal (por defecto Lunes 3AM)
- Backup diferencial: Diario (3AM, excepto día de backup completo)
- Limpieza: Diaria (elimina backups > 90 días)

Configuración en config.py:
- BACKUP_ENABLED: Habilitar/deshabilitar
- BACKUP_FULL_DAY: Día semana backup completo (0=Lunes)
- BACKUP_HOUR: Hora de ejecución
- BACKUP_RETENTION_DAYS: Días de retención
"""

from datetime import date, datetime
from loguru import logger

from database import SessionLocal
from modules.backup.service import BackupService
from config import settings


def ejecutar_backup_completo_wrapper():
    """
    Wrapper para ejecutar backup completo desde el scheduler.
    Se ejecuta semanalmente (por defecto Lunes 3AM).
    """
    logger.info("=" * 60)
    logger.info("🔄 [JOB] Iniciando job de BACKUP COMPLETO semanal")
    logger.info(f"📅 Fecha: {datetime.now()}")
    logger.info("=" * 60)
    
    db = SessionLocal()
    backup_service = BackupService()
    
    try:
        resultado = backup_service.backup_completo(
            db,
            ejecutado_por="SCHEDULER_SEMANAL"
        )
        
        if resultado.exito:
            logger.info("=" * 60)
            logger.info("✅ [JOB] Backup completo realizado exitosamente")
            logger.info(f"   📁 Archivo: {resultado.backup.nombre_archivo}")
            logger.info(f"   💾 Tamaño: {resultado.backup.tamanio_legible}")
            logger.info(f"   📊 Tablas: {resultado.backup.tablas_respaldadas}")
            logger.info(f"   📝 Registros: {resultado.backup.registros_totales}")
            logger.info("=" * 60)
        else:
            logger.error(f"❌ [JOB] Error en backup completo: {resultado.mensaje}")
            
    except Exception as e:
        logger.error(f"❌ [JOB] Error crítico en backup completo: {e}")
        logger.exception(e)
        db.rollback()
    finally:
        db.close()


def ejecutar_backup_diferencial_wrapper():
    """
    Wrapper para ejecutar backup diferencial desde el scheduler.
    Se ejecuta diariamente (excepto el día del backup completo).
    """
    # Verificar si hoy es día de backup completo
    dia_actual = datetime.now().weekday()
    dia_backup_completo = getattr(settings, 'BACKUP_FULL_DAY', 0)
    
    if dia_actual == dia_backup_completo:
        logger.info("⏭️ [JOB] Hoy es día de backup completo, saltando diferencial")
        return
    
    logger.info("=" * 60)
    logger.info("🔄 [JOB] Iniciando job de BACKUP DIFERENCIAL diario")
    logger.info(f"📅 Fecha: {datetime.now()}")
    logger.info("=" * 60)
    
    db = SessionLocal()
    backup_service = BackupService()
    
    try:
        resultado = backup_service.backup_diferencial(
            db,
            ejecutado_por="SCHEDULER_DIARIO"
        )
        
        if resultado.exito:
            logger.info("=" * 60)
            logger.info("✅ [JOB] Backup diferencial realizado exitosamente")
            logger.info(f"   📁 Archivo: {resultado.backup.nombre_archivo}")
            logger.info(f"   💾 Tamaño: {resultado.backup.tamanio_legible}")
            logger.info(f"   📊 Tablas con cambios: {resultado.backup.tablas_respaldadas}")
            logger.info(f"   📝 Registros: {resultado.backup.registros_totales}")
            logger.info("=" * 60)
        else:
            logger.error(f"❌ [JOB] Error en backup diferencial: {resultado.mensaje}")
            
    except Exception as e:
        logger.error(f"❌ [JOB] Error crítico en backup diferencial: {e}")
        logger.exception(e)
        db.rollback()
    finally:
        db.close()


def ejecutar_limpieza_backups_wrapper():
    """
    Wrapper para ejecutar limpieza de backups antiguos desde el scheduler.
    Se ejecuta diariamente y elimina backups > 90 días.
    """
    logger.info("=" * 60)
    logger.info("🧹 [JOB] Iniciando limpieza de backups antiguos")
    logger.info(f"📅 Fecha: {datetime.now()}")
    logger.info(f"⏱️ Retención: {getattr(settings, 'BACKUP_RETENTION_DAYS', 90)} días")
    logger.info("=" * 60)
    
    db = SessionLocal()
    backup_service = BackupService()
    
    try:
        resultado = backup_service.limpiar_backups_antiguos(db)
        
        logger.info("=" * 60)
        logger.info("✅ [JOB] Limpieza de backups completada")
        logger.info(f"   🗑️ Backups eliminados: {resultado.backups_eliminados}")
        logger.info(f"   💾 Espacio liberado: {resultado.espacio_liberado_legible}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ [JOB] Error en limpieza de backups: {e}")
        logger.exception(e)
        db.rollback()
    finally:
        db.close()


def ejecutar_backup_diario_wrapper():
    """
    Job unificado que decide qué tipo de backup ejecutar según el día.
    
    - Lunes (o día configurado): Backup completo
    - Otros días: Backup diferencial
    - Siempre: Limpieza de backups antiguos
    """
    dia_actual = datetime.now().weekday()
    dia_backup_completo = getattr(settings, 'BACKUP_FULL_DAY', 0)
    
    logger.info("=" * 60)
    logger.info("🔄 [JOB] Iniciando job de backup diario")
    logger.info(f"📅 Fecha: {datetime.now()}")
    logger.info(f"📆 Día de la semana: {dia_actual} ({'Backup completo' if dia_actual == dia_backup_completo else 'Backup diferencial'})")
    logger.info("=" * 60)
    
    # 1. Ejecutar backup según corresponda
    if dia_actual == dia_backup_completo:
        logger.info("📦 Ejecutando BACKUP COMPLETO semanal...")
        ejecutar_backup_completo_wrapper()
    else:
        logger.info("📦 Ejecutando BACKUP DIFERENCIAL diario...")
        ejecutar_backup_diferencial_wrapper()
    
    # 2. Siempre ejecutar limpieza
    logger.info("🧹 Ejecutando limpieza de backups antiguos...")
    ejecutar_limpieza_backups_wrapper()
    
    logger.info("=" * 60)
    logger.info("✅ [JOB] Job de backup diario completado")
    logger.info("=" * 60)
