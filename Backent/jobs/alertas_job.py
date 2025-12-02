"""
Job de Alertas Diarias.

Este job se ejecuta diariamente (configurado en scheduler.py) y realiza:
1. Verificar insumos con vencimiento próximo
2. Verificar insumos con stock crítico
3. Crear notificaciones en la tabla `notificaciones`
4. Encolar emails si está configurado
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime
from typing import Optional
from loguru import logger

from database import SessionLocal
from modules.alertas.model import Notificacion
from enums.tipo_alerta import TipoAlertaEnum
from enums.semaforo_estado import SemaforoEstadoEnum
from modules.empresa.model import Empresa, DEFAULT_CONFIGURACION_ALERTAS
from modules.email_service.model import ColaEmail


def ejecutar_alertas_diarias_wrapper():
    """
    Wrapper para ejecutar el job desde el scheduler.
    Crea su propia sesión de BD y maneja el ciclo de vida.
    """
    logger.info("=" * 60)
    logger.info("🔄 [JOB] Iniciando job de alertas diarias")
    logger.info(f"📅 Fecha: {date.today()}")
    logger.info("=" * 60)
    
    db: Session = SessionLocal()
    
    try:
        resultado = ejecutar_alertas_diarias(db, id_empresa=1)
        
        logger.info("=" * 60)
        logger.info("✅ [JOB] Resumen de ejecución:")
        logger.info(f"   📊 Alertas vencimiento: {resultado['alertas_vencimiento']}")
        logger.info(f"   📊 Alertas stock: {resultado['alertas_stock']}")
        logger.info(f"   📧 Emails encolados: {resultado['emails_encolados']}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ [JOB] Error crítico en job de alertas: {e}")
        logger.exception(e)  # Esto loguea el stack trace completo
        db.rollback()
        raise
    finally:
        db.close()


def ejecutar_alertas_diarias(db: Session, id_empresa: int = 1) -> dict:
    """
    Ejecuta la generación de alertas diarias.
    
    Args:
        db: Sesión de base de datos
        id_empresa: ID de la empresa para obtener configuración
        
    Returns:
        Diccionario con estadísticas de ejecución
        
    Raises:
        Exception: Si ocurre un error, hace rollback y propaga la excepción
    """
    resultado = {
        "alertas_vencimiento": 0,
        "alertas_stock": 0,
        "emails_encolados": 0
    }
    
    try:
        # Obtener configuración de la empresa
        config = _obtener_configuracion(db, id_empresa)
        logger.info(f"📋 Configuración cargada: {config}")
        
        # 1. Generar alertas de vencimiento
        alertas_venc = _generar_alertas_vencimiento(db, config)
        resultado["alertas_vencimiento"] = alertas_venc
        
        # 2. Generar alertas de stock crítico
        alertas_stock = _generar_alertas_stock_critico(db, config)
        resultado["alertas_stock"] = alertas_stock
        
        # 3. Encolar email si está configurado
        if config.get("email_alertas"):
            emails = _encolar_email_resumen(
                db,
                email_destino=config["email_alertas"],
                alertas_vencimiento=alertas_venc,
                alertas_stock=alertas_stock
            )
            resultado["emails_encolados"] = emails
        
        # Commit de toda la transacción
        db.commit()
        logger.info("💾 Transacción completada exitosamente")
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Error en job de alertas: {e}")
        db.rollback()
        raise


def _obtener_configuracion(db: Session, id_empresa: int) -> dict:
    """Obtiene configuración de alertas de la empresa."""
    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == id_empresa
    ).first()
    
    if empresa and empresa.configuracion_alertas:
        config = DEFAULT_CONFIGURACION_ALERTAS.copy()
        config.update(empresa.configuracion_alertas)
        return config
    
    return DEFAULT_CONFIGURACION_ALERTAS.copy()


def _generar_alertas_vencimiento(db: Session, config: dict) -> int:
    """
    Genera alertas para lotes próximos a vencer.
    
    Usa SQL puro para la consulta con múltiples joins.
    """
    dias_rojo = config["dias_rojo"]
    dias_amarillo = config["dias_amarillo"]
    
    logger.info(f"🔍 Buscando lotes que vencen en <= {dias_amarillo} días...")
    
    # SQL puro: consulta lotes por vencer (3+ tablas involucradas)
    sql = text("""
        SELECT 
            d.id_ingreso_detalle,
            d.id_insumo,
            d.cantidad_restante,
            d.fecha_vencimiento,
            ins.codigo AS codigo_insumo,
            ins.nombre AS nombre_insumo,
            ins.unidad_medida,
            i.numero_ingreso,
            (d.fecha_vencimiento::date - CURRENT_DATE) AS dias_restantes
        FROM ingresos_insumos_detalle d
        INNER JOIN ingresos_insumos i ON d.id_ingreso = i.id_ingreso
        INNER JOIN insumo ins ON d.id_insumo = ins.id_insumo
        WHERE 
            d.cantidad_restante > 0
            AND d.fecha_vencimiento IS NOT NULL
            AND ins.anulado = false
            AND i.anulado = false
            AND ins.perecible = true
            AND (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_amarillo
        ORDER BY d.fecha_vencimiento ASC
    """)
    
    lotes = db.execute(sql, {"dias_amarillo": dias_amarillo}).fetchall()
    
    logger.info(f"📦 Encontrados {len(lotes)} lotes próximos a vencer")
    
    alertas_creadas = 0
    
    for lote in lotes:
        dias_restantes = lote.dias_restantes
        
        # Determinar tipo de alerta y semáforo
        if dias_restantes < 0:
            tipo = TipoAlertaEnum.VENCIDO
            semaforo = SemaforoEstadoEnum.ROJO
            titulo = f"🔴 VENCIDO: {lote.nombre_insumo}"
            mensaje = (
                f"El insumo '{lote.nombre_insumo}' (Lote: {lote.numero_ingreso}) "
                f"venció hace {abs(dias_restantes)} día(s). "
                f"Cantidad afectada: {lote.cantidad_restante} {lote.unidad_medida}. "
                f"Acción requerida: Retirar del inventario."
            )
        elif dias_restantes <= dias_rojo:
            tipo = TipoAlertaEnum.USAR_HOY
            semaforo = SemaforoEstadoEnum.ROJO
            titulo = f"🔴 USAR HOY: {lote.nombre_insumo}"
            mensaje = (
                f"El insumo '{lote.nombre_insumo}' (Lote: {lote.numero_ingreso}) "
                f"vence en {dias_restantes} día(s). "
                f"Cantidad disponible: {lote.cantidad_restante} {lote.unidad_medida}. "
                f"Acción requerida: Priorizar uso inmediato."
            )
        else:
            tipo = TipoAlertaEnum.VENCIMIENTO_PROXIMO
            semaforo = SemaforoEstadoEnum.AMARILLO
            titulo = f"🟡 Vence pronto: {lote.nombre_insumo}"
            mensaje = (
                f"El insumo '{lote.nombre_insumo}' (Lote: {lote.numero_ingreso}) "
                f"vence en {dias_restantes} días. "
                f"Cantidad disponible: {lote.cantidad_restante} {lote.unidad_medida}. "
                f"Sugerencia: Usar esta semana."
            )
        
        # Verificar si ya existe alerta para este lote hoy
        existe = _verificar_alerta_existente(
            db,
            id_insumo=lote.id_insumo,
            tipo=tipo,
            id_ingreso_detalle=lote.id_ingreso_detalle
        )
        
        if existe:
            logger.debug(f"⏭️ Alerta ya existe para lote {lote.id_ingreso_detalle}")
            continue
        
        # Crear notificación
        notificacion = Notificacion(
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            id_insumo=lote.id_insumo,
            id_ingreso_detalle=lote.id_ingreso_detalle,
            semaforo=semaforo,
            dias_restantes=dias_restantes,
            cantidad_afectada=f"{lote.cantidad_restante} {lote.unidad_medida}"
        )
        db.add(notificacion)
        alertas_creadas += 1
        
        logger.info(
            f"📝 Alerta creada: [{tipo.value}] {lote.nombre_insumo} - "
            f"{dias_restantes} días restantes"
        )
    
    db.flush()
    logger.info(f"✅ {alertas_creadas} alertas de vencimiento creadas")
    
    return alertas_creadas


def _generar_alertas_stock_critico(db: Session, config: dict) -> int:
    """
    Genera alertas para insumos con stock bajo.
    
    Usa SQL puro para agregación con múltiples joins.
    """
    logger.info("🔍 Buscando insumos con stock bajo mínimo...")
    
    # SQL puro: stock actual vs stock mínimo (agregación + joins)
    sql = text("""
        SELECT 
            ins.id_insumo,
            ins.codigo,
            ins.nombre,
            ins.unidad_medida,
            ins.stock_minimo,
            COALESCE(SUM(d.cantidad_restante), 0) AS stock_actual
        FROM insumo ins
        LEFT JOIN ingresos_insumos_detalle d ON ins.id_insumo = d.id_insumo
        LEFT JOIN ingresos_insumos i ON d.id_ingreso = i.id_ingreso AND i.anulado = false
        WHERE 
            ins.anulado = false
        GROUP BY 
            ins.id_insumo, 
            ins.codigo, 
            ins.nombre, 
            ins.unidad_medida, 
            ins.stock_minimo
        HAVING 
            COALESCE(SUM(d.cantidad_restante), 0) < ins.stock_minimo
            AND ins.stock_minimo > 0
        ORDER BY 
            (COALESCE(SUM(d.cantidad_restante), 0) / ins.stock_minimo) ASC
    """)
    
    insumos = db.execute(sql).fetchall()
    
    logger.info(f"📦 Encontrados {len(insumos)} insumos con stock bajo")
    
    alertas_creadas = 0
    
    for insumo in insumos:
        stock_actual = float(insumo.stock_actual)
        stock_minimo = float(insumo.stock_minimo)
        deficit = stock_minimo - stock_actual
        es_critico = stock_actual == 0
        
        # Título y mensaje según criticidad
        if es_critico:
            titulo = f"🔴 SIN STOCK: {insumo.nombre}"
            mensaje = (
                f"El insumo '{insumo.nombre}' ({insumo.codigo}) NO tiene stock disponible. "
                f"Stock mínimo requerido: {stock_minimo} {insumo.unidad_medida}. "
                f"Acción requerida: Realizar compra urgente."
            )
        else:
            porcentaje = round((stock_actual / stock_minimo) * 100, 1)
            titulo = f"🟡 Stock bajo: {insumo.nombre}"
            mensaje = (
                f"El insumo '{insumo.nombre}' ({insumo.codigo}) tiene stock bajo. "
                f"Stock actual: {stock_actual} {insumo.unidad_medida} ({porcentaje}%). "
                f"Stock mínimo: {stock_minimo} {insumo.unidad_medida}. "
                f"Déficit: {deficit} {insumo.unidad_medida}."
            )
        
        # Verificar si ya existe alerta para este insumo hoy
        existe = _verificar_alerta_existente(
            db,
            id_insumo=insumo.id_insumo,
            tipo=TipoAlertaEnum.STOCK_CRITICO
        )
        
        if existe:
            logger.debug(f"⏭️ Alerta de stock ya existe para insumo {insumo.id_insumo}")
            continue
        
        # Crear notificación
        notificacion = Notificacion(
            tipo=TipoAlertaEnum.STOCK_CRITICO,
            titulo=titulo,
            mensaje=mensaje,
            id_insumo=insumo.id_insumo,
            cantidad_afectada=f"Déficit: {deficit} {insumo.unidad_medida}"
        )
        db.add(notificacion)
        alertas_creadas += 1
        
        logger.info(
            f"📝 Alerta creada: [STOCK_CRITICO] {insumo.nombre} - "
            f"Stock: {stock_actual}/{stock_minimo}"
        )
    
    db.flush()
    logger.info(f"✅ {alertas_creadas} alertas de stock creadas")
    
    return alertas_creadas


def _verificar_alerta_existente(
    db: Session,
    id_insumo: int,
    tipo: TipoAlertaEnum,
    id_ingreso_detalle: Optional[int] = None
) -> bool:
    """Verifica si ya existe una alerta activa para evitar duplicados."""
    from sqlalchemy import func
    
    query = db.query(Notificacion).filter(
        Notificacion.id_insumo == id_insumo,
        Notificacion.tipo == tipo,
        Notificacion.activa == True,
        func.date(Notificacion.fecha_creacion) == date.today()
    )
    
    if id_ingreso_detalle:
        query = query.filter(Notificacion.id_ingreso_detalle == id_ingreso_detalle)
    
    return query.first() is not None


def _encolar_email_resumen(
    db: Session,
    email_destino: str,
    alertas_vencimiento: int,
    alertas_stock: int
) -> int:
    """
    Encola un email con el resumen de alertas del día.
    
    Usa la tabla ColaEmail existente.
    """
    if alertas_vencimiento == 0 and alertas_stock == 0:
        logger.info("📧 No hay alertas nuevas, no se enviará email")
        return 0
    
    # Construir cuerpo del email en HTML
    cuerpo_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .alert-box {{ 
                border-left: 4px solid; 
                padding: 15px; 
                margin: 10px 0; 
                background-color: #f9f9f9;
            }}
            .alert-vencimiento {{ border-color: #e74c3c; }}
            .alert-stock {{ border-color: #f39c12; }}
            .footer {{ background-color: #ecf0f1; padding: 15px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Resumen de Alertas - Sistema de Inventario</h1>
            <p>Fecha: {date.today().strftime('%d/%m/%Y')}</p>
        </div>
        
        <div class="content">
            <h2>Resumen del día</h2>
            
            <div class="alert-box alert-vencimiento">
                <h3>🔴 Alertas de Vencimiento: {alertas_vencimiento}</h3>
                <p>Se encontraron {alertas_vencimiento} lotes próximos a vencer o vencidos.</p>
            </div>
            
            <div class="alert-box alert-stock">
                <h3>🟡 Alertas de Stock Crítico: {alertas_stock}</h3>
                <p>Se encontraron {alertas_stock} insumos con stock bajo el mínimo.</p>
            </div>
            
            <p><strong>Total de alertas nuevas: {alertas_vencimiento + alertas_stock}</strong></p>
            
            <p>Por favor, ingrese al sistema para revisar los detalles y tomar las acciones necesarias.</p>
        </div>
        
        <div class="footer">
            <p>Este es un correo automático generado por el Sistema de Inventario.</p>
            <p>No responda a este correo.</p>
        </div>
    </body>
    </html>
    """
    
    # Crear entrada en cola de emails
    email = ColaEmail(
        destinatario=email_destino,
        asunto=f"📊 Alertas de Inventario - {date.today().strftime('%d/%m/%Y')} ({alertas_vencimiento + alertas_stock} nuevas)",
        cuerpo_html=cuerpo_html,
        estado='PENDIENTE'
    )
    db.add(email)
    db.flush()
    
    logger.info(f"📧 Email encolado para: {email_destino}")
    return 1
