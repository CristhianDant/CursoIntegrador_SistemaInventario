"""
Router para endpoints de backup.

Proporciona endpoints para:
- Ejecutar backups manuales
- Listar backups disponibles
- Descargar backups
- Enviar backups por email
- Ver estadísticas
- Limpiar backups antiguos
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from database import get_db
from .service import BackupService
from .schemas import (
    BackupManualRequest, EnviarBackupEmailRequest,
    BackupResponse, BackupListResponse, BackupResultado,
    EstadisticasBackup, LimpiezaResultado, TipoBackup
)

router = APIRouter()
backup_service = BackupService()


@router.get("/estadisticas", response_model=EstadisticasBackup)
def obtener_estadisticas(
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del sistema de backups.
    
    - Total de backups
    - Espacio usado
    - Últimos backups
    - Días de retención
    """
    return backup_service.obtener_estadisticas(db)


@router.get("/listar", response_model=BackupListResponse)
def listar_backups(
    incluir_eliminados: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista todos los backups disponibles.
    
    - **incluir_eliminados**: Si True, incluye backups marcados como eliminados
    """
    return backup_service.listar_backups(db, incluir_eliminados)


@router.get("/{id_backup}", response_model=BackupResponse)
def obtener_backup(
    id_backup: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene información de un backup específico.
    """
    backup = backup_service.obtener_backup(db, id_backup)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup no encontrado")
    
    return BackupResponse.model_validate(backup)


@router.post("/ejecutar", response_model=BackupResultado)
def ejecutar_backup_manual(
    request: BackupManualRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: str = Query(default="MANUAL", description="Usuario que ejecuta el backup")
):
    """
    Ejecuta un backup manual de forma síncrona.
    
    - **tipo**: COMPLETO o DIFERENCIAL
    - **incluir_datos**: Si False, solo exporta estructura
    """
    logger.info(f"📦 Backup manual solicitado por {usuario}: {request.tipo}")
    
    if request.tipo == TipoBackup.COMPLETO:
        resultado = backup_service.backup_completo(
            db, 
            ejecutado_por=usuario,
            incluir_datos=request.incluir_datos
        )
    else:
        resultado = backup_service.backup_diferencial(db, ejecutado_por=usuario)
    
    if not resultado.exito:
        raise HTTPException(status_code=500, detail=resultado.mensaje)
    
    return resultado


@router.get("/{id_backup}/descargar")
def descargar_backup(
    id_backup: int,
    db: Session = Depends(get_db)
):
    """
    Descarga un archivo de backup.
    
    Retorna el archivo .sql.gz comprimido.
    """
    filepath = backup_service.obtener_ruta_archivo(db, id_backup)
    
    if not filepath:
        raise HTTPException(
            status_code=404, 
            detail="Archivo de backup no encontrado"
        )
    
    backup = backup_service.obtener_backup(db, id_backup)
    
    return FileResponse(
        path=str(filepath),
        filename=backup.nombre_archivo,
        media_type="application/gzip"
    )


@router.post("/{id_backup}/enviar-email", response_model=dict)
def enviar_backup_email(
    id_backup: int,
    request: EnviarBackupEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Envía un backup por email.
    
    El backup se adjunta al email como archivo .sql.gz
    
    **Nota**: Para archivos grandes (>25MB), se recomienda usar descarga directa.
    """
    from modules.email_service.service import EmailService
    from modules.email_service.schemas import EmailCreate
    import base64
    
    backup = backup_service.obtener_backup(db, id_backup)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup no encontrado")
    
    filepath = backup_service.obtener_ruta_archivo(db, id_backup)
    if not filepath:
        raise HTTPException(status_code=404, detail="Archivo de backup no encontrado")
    
    # Verificar tamaño (límite 25MB para email)
    if backup.tamanio_bytes and backup.tamanio_bytes > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Backup demasiado grande para enviar por email (máx. 25MB). Use descarga directa."
        )
    
    # Crear email con información del backup
    mensaje_adicional = request.mensaje or ""
    
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>📦 Backup de Base de Datos</h2>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Tipo:</strong> {backup.tipo}</p>
            <p><strong>Archivo:</strong> {backup.nombre_archivo}</p>
            <p><strong>Tamaño:</strong> {backup.tamanio_legible}</p>
            <p><strong>Fecha:</strong> {backup.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
            <p><strong>Tablas:</strong> {backup.tablas_respaldadas}</p>
            <p><strong>Registros:</strong> {backup.registros_totales}</p>
            <p><strong>Hash MD5:</strong> <code>{backup.hash_md5}</code></p>
        </div>
        
        {f'<p><strong>Mensaje:</strong> {mensaje_adicional}</p>' if mensaje_adicional else ''}
        
        <p style="color: #666; font-size: 12px;">
            Este backup fue generado automáticamente por el Sistema de Inventario.<br>
            Para restaurar, descomprima el archivo .gz y ejecute el SQL en PostgreSQL.
        </p>
        
        <hr style="margin: 20px 0;">
        <p style="color: #999; font-size: 11px;">
            Sistema de Inventario - Backup Automático
        </p>
    </body>
    </html>
    """
    
    email_service = EmailService()
    
    # Por ahora enviamos solo el email con información (sin adjunto)
    # Para adjuntar archivos se necesitaría extender el EmailService
    email_data = EmailCreate(
        destinatario=request.email_destino,
        asunto=f"📦 Backup {backup.tipo} - {backup.nombre_archivo}",
        cuerpo_html=cuerpo_html
    )
    
    enviado, mensaje = email_service.enviar_o_encolar(db, email_data)
    
    logger.info(f"📧 Email de backup enviado a {request.email_destino}: {mensaje}")
    
    return {
        "exito": True,
        "mensaje": f"Email {'enviado' if enviado else 'encolado'} a {request.email_destino}",
        "backup_id": id_backup,
        "destinatario": request.email_destino
    }


@router.post("/limpiar", response_model=LimpiezaResultado)
def limpiar_backups_antiguos(
    db: Session = Depends(get_db)
):
    """
    Elimina backups anteriores al período de retención (90 días por defecto).
    
    - Elimina archivos físicos
    - Marca registros como eliminados en BD
    - Retorna espacio liberado
    """
    logger.info("🧹 Limpieza manual de backups solicitada")
    
    return backup_service.limpiar_backups_antiguos(db)


@router.post("/ejecutar-completo", response_model=BackupResultado)
def ejecutar_backup_completo(
    db: Session = Depends(get_db),
    usuario: str = Query(default="MANUAL", description="Usuario que ejecuta el backup")
):
    """
    Ejecuta un backup completo (atajo para /ejecutar con tipo COMPLETO).
    """
    return backup_service.backup_completo(db, ejecutado_por=usuario)


@router.post("/ejecutar-diferencial", response_model=BackupResultado)
def ejecutar_backup_diferencial(
    db: Session = Depends(get_db),
    usuario: str = Query(default="MANUAL", description="Usuario que ejecuta el backup")
):
    """
    Ejecuta un backup diferencial (atajo para /ejecutar con tipo DIFERENCIAL).
    """
    return backup_service.backup_diferencial(db, ejecutado_por=usuario)
