"""Gestor centralizado de auditoría con thread-safety"""

import os
import threading
from pathlib import Path
from datetime import datetime
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class AuditManager:
    """Gestor centralizado para todas las operaciones de auditoría"""
    
    def __init__(self, audit_dir: str = "INFORMES_AUDITORIA"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()  # Recursive lock para thread-safety
        logger.info(f"AuditManager inicializado en {self.audit_dir}")
        
    def create_audit_report(self, operator: str, tracking_info: dict) -> str:
        """
        Crear reporte de auditoría de forma thread-safe
        
        Args:
            operator: Nombre del operador
            tracking_info: Dict con info de rastreo
            
        Returns:
            Ruta del archivo creado
            
        Raises:
            RuntimeError: Si hay error escribiendo el archivo
        """
        with self._lock:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            filename = self.audit_dir / f"AUDITORIA_{timestamp}_{unique_id}.md"
            
            try:
                with open(filename, "w") as f:
                    f.write(f"# INFORME DE AUDITORÍA - {timestamp}\n")
                    f.write(f"OPERADOR: {operator}\n")
                    f.write(f"ID_UNICO: {unique_id}\n")
                    f.write("-" * 80 + "\n")
                    for key, value in tracking_info.items():
                        f.write(f"{key}: {value}\n")
                
                logger.info(f"Reporte creado: {filename}")
                return str(filename)
                
            except IOError as e:
                logger.error(f"Error escribiendo auditoría: {e}")
                raise RuntimeError(f"Error escribiendo auditoría: {e}")
    
    def get_latest_report(self) -> dict:
        """Obtener el último reporte generado
        
        Returns:
            Dict con info del último reporte o None si no existen
        """
        with self._lock:
            reports = sorted(self.audit_dir.glob("AUDITORIA_*.md"))
            if not reports:
                return None
            
            latest = reports[-1]
            return {
                "path": str(latest),
                "filename": latest.name,
                "timestamp": latest.stat().st_mtime,
                "size": latest.stat().st_size
            }
    
    def get_all_reports(self) -> list:
        """Obtener lista de todos los reportes
        
        Returns:
            Lista de rutas de reportes
        """
        with self._lock:
            return sorted([str(r) for r in self.audit_dir.glob("AUDITORIA_*.md")])
    
    def cleanup_old_reports(self, days: int = 7) -> int:
        """Limpiar reportes más antiguos de N días
        
        Args:
            days: Número de días a retener
            
        Returns:
            Número de archivos eliminados
        """
        from datetime import timedelta
        import time
        
        cutoff = time.time() - (days * 86400)
        deleted_count = 0
        
        with self._lock:
            for report in self.audit_dir.glob("AUDITORIA_*.md"):
                try:
                    if report.stat().st_mtime < cutoff:
                        report.unlink()
                        deleted_count += 1
                        logger.info(f"Reporte eliminado: {report.name}")
                except Exception as e:
                    logger.error(f"Error eliminando {report.name}: {e}")
        
        logger.info(f"Limpieza completada: {deleted_count} reportes eliminados")
        return deleted_count
    
    def get_report_count(self) -> int:
        """Obtener cantidad total de reportes
        
        Returns:
            Número de reportes existentes
        """
        with self._lock:
            return len(list(self.audit_dir.glob("AUDITORIA_*.md")))
