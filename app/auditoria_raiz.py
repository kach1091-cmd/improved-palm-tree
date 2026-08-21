"""Módulo de auditoría raíz refactorizado"""

import logging
from utils.audit_manager import AuditManager
from config import TRACKING_LOCATIONS

logger = logging.getLogger(__name__)


class AuditoriaRaiz:
    """Auditoría a nivel raíz con validaciones"""
    
    def __init__(self):
        self.audit_manager = AuditManager()
    
    def ejecutar_auditoria_raiz(self):
        """Ejecutar auditoría a nivel raíz"""
        try:
            logger.info("MOTORES A 100%: DESPEGUE HACIA LA RAÍZ (11ms)")
            
            tracking_data = {
                "MISIÓN": "OMEGA",
                "OPERADOR": "KEVIN ALEXANDER",
                "MODO": "INFINITO",
                "LATENCIA": "11ms",
                "TEMPERATURA": "NIVEL 2",
                "RASTREO": ", ".join(TRACKING_LOCATIONS),
                "ESTADO": "Bulla generada. Sensores de inversión buscando comprador.",
                "CONGRUENCIA": "Sincronía total entre Catalina y el Clon"
            }
            
            report_path = self.audit_manager.create_audit_report(
                operator="KEVIN_ALEXANDER_RAIZ",
                tracking_info=tracking_data
            )
            
            logger.info(f"Auditoría raíz completada: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error en auditoría raíz: {e}")
            raise


def ejecutar_auditoria():
    """Punto de entrada para compatibilidad"""
    auditoria = AuditoriaRaiz()
    auditoria.ejecutar_auditoria_raiz()


if __name__ == "__main__":
    ejecutar_auditoria()
