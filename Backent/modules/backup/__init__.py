"""
Módulo de Backup del Sistema.

Proporciona funcionalidades para:
- Backups completos semanales de la base de datos
- Backups diferenciales diarios
- Compresión y almacenamiento local
- Descarga y envío por email de backups
- Limpieza automática de backups antiguos (>90 días)
"""

from .service import BackupService
from .model import HistorialBackup
from .schemas import BackupResponse, BackupListResponse

__all__ = [
    "BackupService",
    "HistorialBackup",
    "BackupResponse",
    "BackupListResponse"
]
