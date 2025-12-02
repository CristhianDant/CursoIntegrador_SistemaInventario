"""
Configuración del Scheduler de Tareas Programadas.

Utiliza APScheduler para ejecutar jobs CRON de manera automática.
Los jobs se ejecutan diariamente según la configuración de la empresa.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from loguru import logger

from config import settings

# Instancia global del scheduler
scheduler = BackgroundScheduler(
    job_defaults={
        'coalesce': True,           # Si se perdieron ejecuciones, ejecutar solo una vez
        'max_instances': 1,          # Evitar ejecuciones paralelas del mismo job
        'misfire_grace_time': 3600   # 1 hora de gracia si se perdió la ejecución
    },
    timezone='America/Lima'  # Ajustar a tu zona horaria
)


def job_listener(event):
    """Listener para eventos de jobs (éxito o error)."""
    if event.exception:
        logger.error(
            f"❌ Job {event.job_id} falló con excepción: {event.exception}",
            exc_info=event.exception
        )
    else:
        logger.info(f"✅ Job {event.job_id} ejecutado exitosamente")


def init_scheduler():
    """
    Inicializa y configura los jobs del scheduler.
    
    Se debe llamar al inicio de la aplicación.
    """
    from jobs.alertas_job import ejecutar_alertas_diarias_wrapper
    
    # Agregar listener para logging de eventos
    scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    
    # Job diario de alertas
    hora = settings.SCHEDULER_HORA_DEFAULT
    minuto = settings.SCHEDULER_MINUTO_DEFAULT
    
    scheduler.add_job(
        ejecutar_alertas_diarias_wrapper,
        trigger=CronTrigger(hour=hora, minute=minuto),
        id="alertas_diarias",
        name="Generar alertas diarias (vencimiento y stock)",
        replace_existing=True
    )
    
    logger.info(
        f"📅 Scheduler configurado: Job 'alertas_diarias' programado para las {hora:02d}:{minuto:02d}"
    )


def start_scheduler():
    """
    Inicia el scheduler si está habilitado en la configuración.
    """
    if not settings.SCHEDULER_ENABLED:
        logger.warning("⚠️ Scheduler deshabilitado en configuración (SCHEDULER_ENABLED=false)")
        return
    
    if not scheduler.running:
        scheduler.start()
        logger.info("🚀 Scheduler iniciado correctamente")
        
        # Mostrar jobs programados
        jobs = scheduler.get_jobs()
        for job in jobs:
            logger.info(f"   📌 Job: {job.id} - Próxima ejecución: {job.next_run_time}")


def shutdown_scheduler():
    """
    Detiene el scheduler de forma segura.
    
    Se debe llamar al cerrar la aplicación.
    """
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("🛑 Scheduler detenido correctamente")


def get_scheduler_status() -> dict:
    """
    Obtiene el estado actual del scheduler.
    
    Returns:
        Diccionario con información del scheduler y jobs.
    """
    jobs_info = []
    
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
    
    return {
        "running": scheduler.running,
        "enabled": settings.SCHEDULER_ENABLED,
        "jobs": jobs_info
    }


def ejecutar_job_ahora(job_id: str = "alertas_diarias"):
    """
    Ejecuta un job inmediatamente (fuera del schedule).
    
    Args:
        job_id: ID del job a ejecutar.
    """
    job = scheduler.get_job(job_id)
    if job:
        logger.info(f"🔄 Ejecutando job '{job_id}' manualmente...")
        job.modify(next_run_time=None)  # Ejecutar ahora
        return True
    
    logger.warning(f"⚠️ Job '{job_id}' no encontrado")
    return False
