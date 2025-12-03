"""
Servicio de Backup de Base de Datos.

Realiza backups de PostgreSQL usando SQLAlchemy para exportar
datos en formato SQL, sin depender de pg_dump (útil cuando la BD
está en un contenedor Docker separado).

Estrategia:
- Backup completo: Exporta estructura + todos los datos de todas las tablas
- Backup diferencial: Exporta solo registros modificados desde el último backup completo
"""

import os
import gzip
import hashlib
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect, MetaData
from sqlalchemy.engine import Engine
from loguru import logger

from config import settings
from database import engine, Base
from .model import HistorialBackup
from .schemas import (
    TipoBackup, EstadoBackup, BackupResponse, 
    BackupListResponse, BackupResultado, EstadisticasBackup,
    LimpiezaResultado
)


class BackupService:
    """
    Servicio para gestión de backups de base de datos PostgreSQL.
    
    Características:
    - Backups completos semanales
    - Backups diferenciales diarios
    - Compresión con gzip
    - Retención configurable (default: 90 días)
    - Verificación de integridad con MD5
    """
    
    def __init__(self, backup_path: Optional[str] = None):
        """
        Inicializa el servicio de backup.
        
        Args:
            backup_path: Ruta donde almacenar backups. 
                        Si es None, usa BACKUP_PATH de config o 'backups/'
        """
        self.backup_path = Path(backup_path or getattr(settings, 'BACKUP_PATH', 'backups'))
        self.retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 90)
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self):
        """Crea el directorio de backups si no existe."""
        self.backup_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directorio de backups: {self.backup_path.absolute()}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatea bytes a formato legible (KB, MB, GB)."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calcula el hash MD5 de un archivo."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_all_tables(self, db: Session) -> List[str]:
        """Obtiene lista de todas las tablas en la BD."""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        # Excluir tablas de sistema y alembic
        excluded = {'alembic_version'}
        return [t for t in tables if t not in excluded]
    
    def _escape_value(self, value: Any) -> str:
        """Escapa un valor para inserción SQL."""
        if value is None:
            return 'NULL'
        elif isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"
        elif isinstance(value, bytes):
            return f"E'\\\\x{value.hex()}'"
        else:
            # Escapar comillas simples
            escaped = str(value).replace("'", "''")
            return f"'{escaped}'"
    
    def _export_table_data(self, db: Session, table_name: str) -> Tuple[str, int]:
        """
        Exporta los datos de una tabla a formato SQL INSERT.
        
        Returns:
            Tuple[str, int]: (SQL statements, número de registros)
        """
        try:
            result = db.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
            
            if not rows:
                return "", 0
            
            sql_lines = []
            for row in rows:
                values = [self._escape_value(v) for v in row]
                sql_lines.append(
                    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
                )
            
            return "\n".join(sql_lines), len(rows)
            
        except Exception as e:
            logger.error(f"Error exportando tabla {table_name}: {e}")
            return f"-- Error exportando {table_name}: {e}\n", 0
    
    def _export_table_structure(self, table_name: str) -> str:
        """
        Genera el SQL de creación de una tabla.
        """
        inspector = inspect(engine)
        
        try:
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            fk_constraints = inspector.get_foreign_keys(table_name)
            
            column_defs = []
            for col in columns:
                col_def = f"    {col['name']} {col['type']}"
                if not col.get('nullable', True):
                    col_def += " NOT NULL"
                if col.get('default') is not None:
                    col_def += f" DEFAULT {col['default']}"
                column_defs.append(col_def)
            
            # Primary key
            if pk_constraint and pk_constraint.get('constrained_columns'):
                pk_cols = ', '.join(pk_constraint['constrained_columns'])
                column_defs.append(f"    PRIMARY KEY ({pk_cols})")
            
            # Foreign keys
            for fk in fk_constraints:
                fk_cols = ', '.join(fk['constrained_columns'])
                ref_table = fk['referred_table']
                ref_cols = ', '.join(fk['referred_columns'])
                column_defs.append(
                    f"    FOREIGN KEY ({fk_cols}) REFERENCES {ref_table} ({ref_cols})"
                )
            
            create_sql = f"""
-- Tabla: {table_name}
DROP TABLE IF EXISTS {table_name} CASCADE;
CREATE TABLE {table_name} (
{','.join(chr(10).join(column_defs) if column_defs else '')}
);
"""
            return create_sql
            
        except Exception as e:
            logger.error(f"Error generando estructura de {table_name}: {e}")
            return f"-- Error generando estructura de {table_name}: {e}\n"
    
    def backup_completo(
        self,
        db: Session,
        ejecutado_por: str = "SCHEDULER",
        incluir_datos: bool = True
    ) -> BackupResultado:
        """
        Realiza un backup completo de la base de datos.
        
        Args:
            db: Sesión de base de datos
            ejecutado_por: Quién ejecuta el backup (SCHEDULER, MANUAL, usuario)
            incluir_datos: Si True, incluye datos; si False, solo estructura
            
        Returns:
            BackupResultado con información del backup
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}_FULL.sql.gz"
        filepath = self.backup_path / filename
        
        logger.info(f"🔄 Iniciando backup completo: {filename}")
        start_time = time.time()
        
        # Crear registro en BD con estado EN_PROCESO
        backup_record = HistorialBackup(
            tipo=TipoBackup.COMPLETO.value,
            nombre_archivo=filename,
            ruta_archivo=str(filepath.absolute()),
            estado=EstadoBackup.EN_PROCESO.value,
            ejecutado_por=ejecutado_por
        )
        db.add(backup_record)
        db.commit()
        db.refresh(backup_record)
        
        try:
            tables = self._get_all_tables(db)
            total_registros = 0
            
            # Generar contenido SQL
            sql_content = []
            sql_content.append(f"-- Backup Completo del Sistema de Inventario")
            sql_content.append(f"-- Fecha: {datetime.now().isoformat()}")
            sql_content.append(f"-- Base de datos: {settings.POST_DB}")
            sql_content.append(f"-- Tablas: {len(tables)}")
            sql_content.append(f"-- Ejecutado por: {ejecutado_por}")
            sql_content.append("")
            sql_content.append("SET client_encoding = 'UTF8';")
            sql_content.append("SET standard_conforming_strings = on;")
            sql_content.append("BEGIN;")
            sql_content.append("")
            
            for table in tables:
                logger.debug(f"  Exportando tabla: {table}")
                
                # Estructura
                sql_content.append(self._export_table_structure(table))
                
                # Datos
                if incluir_datos:
                    data_sql, count = self._export_table_data(db, table)
                    if data_sql:
                        sql_content.append(f"-- Datos de {table} ({count} registros)")
                        sql_content.append(data_sql)
                        sql_content.append("")
                    total_registros += count
            
            sql_content.append("COMMIT;")
            sql_content.append(f"-- Fin del backup. Total registros: {total_registros}")
            
            # Escribir archivo comprimido
            full_sql = "\n".join(sql_content)
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(full_sql)
            
            # Calcular métricas
            duration = time.time() - start_time
            file_size = filepath.stat().st_size
            md5_hash = self._calculate_md5(filepath)
            
            # Actualizar registro
            backup_record.estado = EstadoBackup.COMPLETADO.value
            backup_record.tamanio_bytes = file_size
            backup_record.tamanio_legible = self._format_size(file_size)
            backup_record.duracion_segundos = round(duration, 2)
            backup_record.tablas_respaldadas = len(tables)
            backup_record.registros_totales = total_registros
            backup_record.hash_md5 = md5_hash
            db.commit()
            
            logger.info(f"✅ Backup completo exitoso: {filename}")
            logger.info(f"   📊 Tablas: {len(tables)}, Registros: {total_registros}")
            logger.info(f"   💾 Tamaño: {self._format_size(file_size)}")
            logger.info(f"   ⏱️ Duración: {duration:.2f}s")
            
            # Crear notificación
            self._crear_notificacion_backup(db, backup_record, True)
            
            return BackupResultado(
                exito=True,
                mensaje=f"Backup completo realizado exitosamente",
                backup=BackupResponse.model_validate(backup_record)
            )
            
        except Exception as e:
            logger.error(f"❌ Error en backup completo: {e}")
            backup_record.estado = EstadoBackup.ERROR.value
            backup_record.mensaje_error = str(e)
            backup_record.duracion_segundos = time.time() - start_time
            db.commit()
            
            # Crear notificación de error
            self._crear_notificacion_backup(db, backup_record, False, str(e))
            
            return BackupResultado(
                exito=False,
                mensaje=f"Error en backup: {str(e)}",
                backup=None
            )
    
    def backup_diferencial(
        self,
        db: Session,
        ejecutado_por: str = "SCHEDULER"
    ) -> BackupResultado:
        """
        Realiza un backup diferencial (solo cambios desde el último backup completo).
        
        Para simplicidad, exporta todos los registros de tablas con campos de auditoría
        que hayan sido modificados desde el último backup completo.
        
        Args:
            db: Sesión de base de datos
            ejecutado_por: Quién ejecuta el backup
            
        Returns:
            BackupResultado con información del backup
        """
        # Obtener último backup completo
        ultimo_completo = db.query(HistorialBackup).filter(
            HistorialBackup.tipo == TipoBackup.COMPLETO.value,
            HistorialBackup.estado == EstadoBackup.COMPLETADO.value,
            HistorialBackup.eliminado == False
        ).order_by(HistorialBackup.fecha_creacion.desc()).first()
        
        if not ultimo_completo:
            logger.warning("⚠️ No hay backup completo previo, realizando backup completo")
            return self.backup_completo(db, ejecutado_por)
        
        fecha_base = ultimo_completo.fecha_creacion
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}_DIFF.sql.gz"
        filepath = self.backup_path / filename
        
        logger.info(f"🔄 Iniciando backup diferencial: {filename}")
        logger.info(f"   Base: {ultimo_completo.nombre_archivo} ({fecha_base})")
        start_time = time.time()
        
        # Crear registro en BD
        backup_record = HistorialBackup(
            tipo=TipoBackup.DIFERENCIAL.value,
            nombre_archivo=filename,
            ruta_archivo=str(filepath.absolute()),
            estado=EstadoBackup.EN_PROCESO.value,
            ejecutado_por=ejecutado_por,
            id_backup_base=ultimo_completo.id_backup
        )
        db.add(backup_record)
        db.commit()
        db.refresh(backup_record)
        
        try:
            tables = self._get_all_tables(db)
            total_registros = 0
            tablas_con_cambios = 0
            
            # Campos de auditoría comunes
            audit_fields = ['fecha_creacion', 'fecha_actualizacion', 'created_at', 'updated_at', 'fecha_modificacion']
            
            sql_content = []
            sql_content.append(f"-- Backup Diferencial del Sistema de Inventario")
            sql_content.append(f"-- Fecha: {datetime.now().isoformat()}")
            sql_content.append(f"-- Base de datos: {settings.POST_DB}")
            sql_content.append(f"-- Backup base: {ultimo_completo.nombre_archivo}")
            sql_content.append(f"-- Cambios desde: {fecha_base.isoformat()}")
            sql_content.append(f"-- Ejecutado por: {ejecutado_por}")
            sql_content.append("")
            sql_content.append("SET client_encoding = 'UTF8';")
            sql_content.append("SET standard_conforming_strings = on;")
            sql_content.append("BEGIN;")
            sql_content.append("")
            
            inspector = inspect(engine)
            
            for table in tables:
                try:
                    columns = inspector.get_columns(table)
                    col_names = [c['name'] for c in columns]
                    
                    # Buscar campo de auditoría
                    audit_col = None
                    for field in audit_fields:
                        if field in col_names:
                            audit_col = field
                            break
                    
                    if audit_col:
                        # Exportar solo registros nuevos/modificados
                        query = text(
                            f"SELECT * FROM {table} WHERE {audit_col} >= :fecha_base"
                        )
                        result = db.execute(query, {"fecha_base": fecha_base})
                    else:
                        # Si no tiene campo de auditoría, exportar todo
                        result = db.execute(text(f"SELECT * FROM {table}"))
                    
                    rows = result.fetchall()
                    result_columns = result.keys()
                    
                    if rows:
                        tablas_con_cambios += 1
                        sql_content.append(f"-- Cambios en {table} ({len(rows)} registros)")
                        
                        for row in rows:
                            values = [self._escape_value(v) for v in row]
                            # Usar UPSERT (INSERT ... ON CONFLICT)
                            pk_constraint = inspector.get_pk_constraint(table)
                            pk_cols = pk_constraint.get('constrained_columns', []) if pk_constraint else []
                            
                            if pk_cols:
                                pk_list = ', '.join(pk_cols)
                                update_cols = [f"{c} = EXCLUDED.{c}" for c in result_columns if c not in pk_cols]
                                sql_content.append(
                                    f"INSERT INTO {table} ({', '.join(result_columns)}) "
                                    f"VALUES ({', '.join(values)}) "
                                    f"ON CONFLICT ({pk_list}) DO UPDATE SET {', '.join(update_cols)};"
                                )
                            else:
                                sql_content.append(
                                    f"INSERT INTO {table} ({', '.join(result_columns)}) VALUES ({', '.join(values)});"
                                )
                        
                        sql_content.append("")
                        total_registros += len(rows)
                        
                except Exception as e:
                    sql_content.append(f"-- Error procesando {table}: {e}")
                    logger.warning(f"Error en tabla {table}: {e}")
            
            sql_content.append("COMMIT;")
            sql_content.append(f"-- Fin del backup diferencial. Total registros: {total_registros}")
            
            # Escribir archivo comprimido
            full_sql = "\n".join(sql_content)
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(full_sql)
            
            # Calcular métricas
            duration = time.time() - start_time
            file_size = filepath.stat().st_size
            md5_hash = self._calculate_md5(filepath)
            
            # Actualizar registro
            backup_record.estado = EstadoBackup.COMPLETADO.value
            backup_record.tamanio_bytes = file_size
            backup_record.tamanio_legible = self._format_size(file_size)
            backup_record.duracion_segundos = round(duration, 2)
            backup_record.tablas_respaldadas = tablas_con_cambios
            backup_record.registros_totales = total_registros
            backup_record.hash_md5 = md5_hash
            db.commit()
            
            logger.info(f"✅ Backup diferencial exitoso: {filename}")
            logger.info(f"   📊 Tablas con cambios: {tablas_con_cambios}, Registros: {total_registros}")
            logger.info(f"   💾 Tamaño: {self._format_size(file_size)}")
            logger.info(f"   ⏱️ Duración: {duration:.2f}s")
            
            return BackupResultado(
                exito=True,
                mensaje=f"Backup diferencial realizado exitosamente",
                backup=BackupResponse.model_validate(backup_record)
            )
            
        except Exception as e:
            logger.error(f"❌ Error en backup diferencial: {e}")
            backup_record.estado = EstadoBackup.ERROR.value
            backup_record.mensaje_error = str(e)
            backup_record.duracion_segundos = time.time() - start_time
            db.commit()
            
            return BackupResultado(
                exito=False,
                mensaje=f"Error en backup diferencial: {str(e)}",
                backup=None
            )
    
    def _crear_notificacion_backup(
        self,
        db: Session,
        backup: HistorialBackup,
        exito: bool,
        error: Optional[str] = None
    ):
        """Crea una notificación para el resultado del backup."""
        from modules.alertas.model import Notificacion
        
        if exito:
            titulo = f"✅ Backup {backup.tipo} completado"
            mensaje = (
                f"Backup realizado exitosamente.\n"
                f"Archivo: {backup.nombre_archivo}\n"
                f"Tamaño: {backup.tamanio_legible}\n"
                f"Tablas: {backup.tablas_respaldadas}\n"
                f"Registros: {backup.registros_totales}"
            )
            semaforo = "VERDE"
        else:
            titulo = f"❌ Error en Backup {backup.tipo}"
            mensaje = f"Error al realizar backup: {error}"
            semaforo = "ROJO"
        
        notificacion = Notificacion(
            tipo="BACKUP",
            titulo=titulo,
            mensaje=mensaje,
            semaforo=semaforo,
            leida=False,
            activa=True
        )
        db.add(notificacion)
        db.commit()
    
    def listar_backups(
        self,
        db: Session,
        incluir_eliminados: bool = False
    ) -> BackupListResponse:
        """
        Lista todos los backups disponibles.
        
        Args:
            db: Sesión de base de datos
            incluir_eliminados: Si True, incluye backups marcados como eliminados
            
        Returns:
            BackupListResponse con lista de backups
        """
        query = db.query(HistorialBackup)
        
        if not incluir_eliminados:
            query = query.filter(HistorialBackup.eliminado == False)
        
        backups = query.order_by(HistorialBackup.fecha_creacion.desc()).all()
        
        # Calcular espacio total
        espacio_total = sum(b.tamanio_bytes or 0 for b in backups)
        
        return BackupListResponse(
            total=len(backups),
            backups=[BackupResponse.model_validate(b) for b in backups],
            espacio_total_usado=self._format_size(espacio_total)
        )
    
    def obtener_backup(self, db: Session, id_backup: int) -> Optional[HistorialBackup]:
        """Obtiene un backup por ID."""
        return db.query(HistorialBackup).filter(
            HistorialBackup.id_backup == id_backup,
            HistorialBackup.eliminado == False
        ).first()
    
    def obtener_ruta_archivo(self, db: Session, id_backup: int) -> Optional[Path]:
        """
        Obtiene la ruta del archivo de backup si existe.
        
        Returns:
            Path al archivo o None si no existe
        """
        backup = self.obtener_backup(db, id_backup)
        if not backup:
            return None
        
        filepath = Path(backup.ruta_archivo)
        if filepath.exists():
            return filepath
        
        return None
    
    def limpiar_backups_antiguos(self, db: Session) -> LimpiezaResultado:
        """
        Elimina backups más antiguos que el período de retención.
        
        Returns:
            LimpiezaResultado con información de la limpieza
        """
        fecha_limite = datetime.now() - timedelta(days=self.retention_days)
        
        logger.info(f"🧹 Limpiando backups anteriores a {fecha_limite.date()}")
        
        # Obtener backups a eliminar
        backups_antiguos = db.query(HistorialBackup).filter(
            HistorialBackup.fecha_creacion < fecha_limite,
            HistorialBackup.eliminado == False
        ).all()
        
        archivos_eliminados = []
        espacio_liberado = 0
        
        for backup in backups_antiguos:
            try:
                filepath = Path(backup.ruta_archivo)
                
                # Eliminar archivo físico
                if filepath.exists():
                    file_size = filepath.stat().st_size
                    filepath.unlink()
                    espacio_liberado += file_size
                    archivos_eliminados.append(backup.nombre_archivo)
                    logger.info(f"   🗑️ Eliminado: {backup.nombre_archivo}")
                
                # Marcar como eliminado en BD
                backup.eliminado = True
                backup.fecha_eliminacion = datetime.now()
                
            except Exception as e:
                logger.error(f"Error eliminando {backup.nombre_archivo}: {e}")
        
        db.commit()
        
        resultado = LimpiezaResultado(
            backups_eliminados=len(archivos_eliminados),
            espacio_liberado_bytes=espacio_liberado,
            espacio_liberado_legible=self._format_size(espacio_liberado),
            archivos_eliminados=archivos_eliminados
        )
        
        logger.info(f"✅ Limpieza completada: {resultado.backups_eliminados} backups eliminados, {resultado.espacio_liberado_legible} liberados")
        
        return resultado
    
    def obtener_estadisticas(self, db: Session) -> EstadisticasBackup:
        """
        Obtiene estadísticas del sistema de backups.
        
        Returns:
            EstadisticasBackup con métricas
        """
        backups = db.query(HistorialBackup).filter(
            HistorialBackup.eliminado == False
        ).all()
        
        completos = [b for b in backups if b.tipo == TipoBackup.COMPLETO.value]
        diferenciales = [b for b in backups if b.tipo == TipoBackup.DIFERENCIAL.value]
        
        espacio_total = sum(b.tamanio_bytes or 0 for b in backups)
        
        ultimo_completo = max(
            [b.fecha_creacion for b in completos], 
            default=None
        )
        ultimo_diferencial = max(
            [b.fecha_creacion for b in diferenciales], 
            default=None
        )
        
        return EstadisticasBackup(
            total_backups=len(backups),
            backups_completos=len(completos),
            backups_diferenciales=len(diferenciales),
            espacio_usado_bytes=espacio_total,
            espacio_usado_legible=self._format_size(espacio_total),
            ultimo_backup_completo=ultimo_completo,
            ultimo_backup_diferencial=ultimo_diferencial,
            proxima_limpieza=datetime.now() + timedelta(days=1),  # Diaria
            dias_retencion=self.retention_days
        )
