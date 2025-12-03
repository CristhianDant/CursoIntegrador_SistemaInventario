"""
Job de Mantenimiento de Logs.

Este job se ejecuta diariamente y realiza:
1. Compresión de logs antiguos (> 7 días por defecto)
2. Eliminación de logs comprimidos antiguos (> 90 días)

Configuración en config.py:
- LOGS_COMPRESSION_ENABLED: Habilitar/deshabilitar
- LOGS_COMPRESSION_DAYS: Días antes de comprimir
- LOGS_RETENTION_DAYS: Días de retención de comprimidos
- LOGS_PATH: Directorio de logs
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
from loguru import logger

from config import settings


class LogsMaintenanceService:
    """
    Servicio para mantenimiento de archivos de log.
    
    Características:
    - Compresión de logs antiguos con gzip
    - Eliminación de logs comprimidos expirados
    - Preservación de logs actuales
    """
    
    def __init__(self, logs_path: str = None):
        """
        Inicializa el servicio.
        
        Args:
            logs_path: Ruta al directorio de logs
        """
        self.logs_path = Path(logs_path or getattr(settings, 'LOGS_PATH', 'logs'))
        self.compression_days = getattr(settings, 'LOGS_COMPRESSION_DAYS', 7)
        self.retention_days = getattr(settings, 'LOGS_RETENTION_DAYS', 90)
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatea bytes a formato legible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _get_file_age_days(self, filepath: Path) -> int:
        """Obtiene la antigüedad de un archivo en días."""
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        return (datetime.now() - mtime).days
    
    def _should_compress(self, filepath: Path) -> bool:
        """
        Determina si un archivo de log debe comprimirse.
        
        Criterios:
        - Es un archivo .log
        - Tiene más de X días de antigüedad
        - No es el archivo de log activo (con fecha de hoy en nombre)
        """
        if not filepath.suffix == '.log':
            return False
        
        # No comprimir si ya está comprimido
        if filepath.suffix == '.gz':
            return False
        
        # Verificar antigüedad
        age_days = self._get_file_age_days(filepath)
        if age_days < self.compression_days:
            return False
        
        # No comprimir logs del día actual
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in filepath.name:
            return False
        
        return True
    
    def _should_delete(self, filepath: Path) -> bool:
        """
        Determina si un archivo comprimido debe eliminarse.
        
        Criterios:
        - Es un archivo .gz
        - Tiene más de X días de antigüedad
        """
        if not filepath.suffix == '.gz':
            return False
        
        age_days = self._get_file_age_days(filepath)
        return age_days > self.retention_days
    
    def comprimir_logs_antiguos(self) -> Tuple[int, int, List[str]]:
        """
        Comprime logs más antiguos que el período configurado.
        
        Returns:
            Tuple[int, int, List[str]]: (archivos_comprimidos, bytes_ahorrados, lista_archivos)
        """
        if not self.logs_path.exists():
            logger.warning(f"⚠️ Directorio de logs no existe: {self.logs_path}")
            return 0, 0, []
        
        archivos_comprimidos = 0
        bytes_ahorrados = 0
        archivos_procesados = []
        
        for filepath in self.logs_path.glob("*.log*"):
            if filepath.is_file() and self._should_compress(filepath):
                try:
                    original_size = filepath.stat().st_size
                    compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
                    
                    # Comprimir archivo
                    with open(filepath, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    compressed_size = compressed_path.stat().st_size
                    ahorro = original_size - compressed_size
                    
                    # Eliminar archivo original
                    filepath.unlink()
                    
                    archivos_comprimidos += 1
                    bytes_ahorrados += ahorro
                    archivos_procesados.append(filepath.name)
                    
                    logger.debug(
                        f"   📦 Comprimido: {filepath.name} "
                        f"({self._format_size(original_size)} → {self._format_size(compressed_size)})"
                    )
                    
                except Exception as e:
                    logger.error(f"Error comprimiendo {filepath.name}: {e}")
        
        return archivos_comprimidos, bytes_ahorrados, archivos_procesados
    
    def eliminar_logs_antiguos(self) -> Tuple[int, int, List[str]]:
        """
        Elimina logs comprimidos más antiguos que el período de retención.
        
        Returns:
            Tuple[int, int, List[str]]: (archivos_eliminados, bytes_liberados, lista_archivos)
        """
        if not self.logs_path.exists():
            return 0, 0, []
        
        archivos_eliminados = 0
        bytes_liberados = 0
        archivos_procesados = []
        
        for filepath in self.logs_path.glob("*.gz"):
            if filepath.is_file() and self._should_delete(filepath):
                try:
                    file_size = filepath.stat().st_size
                    filepath.unlink()
                    
                    archivos_eliminados += 1
                    bytes_liberados += file_size
                    archivos_procesados.append(filepath.name)
                    
                    logger.debug(f"   🗑️ Eliminado: {filepath.name}")
                    
                except Exception as e:
                    logger.error(f"Error eliminando {filepath.name}: {e}")
        
        return archivos_eliminados, bytes_liberados, archivos_procesados
    
    def ejecutar_mantenimiento(self) -> dict:
        """
        Ejecuta el mantenimiento completo de logs.
        
        Returns:
            dict con resumen de operaciones
        """
        resultado = {
            "archivos_comprimidos": 0,
            "bytes_ahorrados": 0,
            "archivos_comprimidos_lista": [],
            "archivos_eliminados": 0,
            "bytes_liberados": 0,
            "archivos_eliminados_lista": [],
            "espacio_total_recuperado": 0,
            "espacio_total_legible": "0 B"
        }
        
        # 1. Comprimir logs antiguos
        comprimidos, ahorrados, lista_comp = self.comprimir_logs_antiguos()
        resultado["archivos_comprimidos"] = comprimidos
        resultado["bytes_ahorrados"] = ahorrados
        resultado["archivos_comprimidos_lista"] = lista_comp
        
        # 2. Eliminar logs comprimidos antiguos
        eliminados, liberados, lista_elim = self.eliminar_logs_antiguos()
        resultado["archivos_eliminados"] = eliminados
        resultado["bytes_liberados"] = liberados
        resultado["archivos_eliminados_lista"] = lista_elim
        
        # 3. Calcular totales
        espacio_total = ahorrados + liberados
        resultado["espacio_total_recuperado"] = espacio_total
        resultado["espacio_total_legible"] = self._format_size(espacio_total)
        
        return resultado


def ejecutar_mantenimiento_logs_wrapper():
    """
    Wrapper para ejecutar mantenimiento de logs desde el scheduler.
    Se ejecuta diariamente (por defecto a las 4 AM).
    """
    if not getattr(settings, 'LOGS_COMPRESSION_ENABLED', True):
        logger.info("⏭️ [JOB] Mantenimiento de logs deshabilitado en configuración")
        return
    
    logger.info("=" * 60)
    logger.info("🧹 [JOB] Iniciando mantenimiento de logs")
    logger.info(f"📅 Fecha: {datetime.now()}")
    logger.info(f"⏱️ Comprimir logs > {getattr(settings, 'LOGS_COMPRESSION_DAYS', 7)} días")
    logger.info(f"🗑️ Eliminar comprimidos > {getattr(settings, 'LOGS_RETENTION_DAYS', 90)} días")
    logger.info("=" * 60)
    
    try:
        service = LogsMaintenanceService()
        resultado = service.ejecutar_mantenimiento()
        
        logger.info("=" * 60)
        logger.info("✅ [JOB] Mantenimiento de logs completado")
        logger.info(f"   📦 Archivos comprimidos: {resultado['archivos_comprimidos']}")
        logger.info(f"   💾 Espacio ahorrado: {service._format_size(resultado['bytes_ahorrados'])}")
        logger.info(f"   🗑️ Archivos eliminados: {resultado['archivos_eliminados']}")
        logger.info(f"   💾 Espacio liberado: {service._format_size(resultado['bytes_liberados'])}")
        logger.info(f"   📊 Total recuperado: {resultado['espacio_total_legible']}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ [JOB] Error en mantenimiento de logs: {e}")
        logger.exception(e)
