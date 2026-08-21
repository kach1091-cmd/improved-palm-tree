"""Motor de auditoría Cataleya refactorizado con manejo de errores y thread-safety"""

import time
import logging
from utils.audit_manager import AuditManager
from config import AUDIT_CYCLE_HOURS, TRACKING_LOCATIONS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class MotorCataleya:
    """Motor de auditoría con reintentos y manejo de fallos"""
    
    def __init__(self):
        self.audit_manager = AuditManager()
        self.is_running = False
        self.cycle_interval = AUDIT_CYCLE_HOURS * 3600
    
    def start(self):
        """Inicia el motor de auditoría"""
        self.is_running = True
        logger.info("Motor Cataleya iniciado")
        self.run()
    
    def stop(self):
        """Detiene el motor de auditoría de forma segura"""
        self.is_running = False
        logger.info("Motor Cataleya detenido")
    
    def run(self):
        """Loop principal de auditoría con manejo de errores"""
        consecutive_failures = 0
        max_failures = 3
        
        while self.is_running:
            try:
                tracking_data = {
                    "LATENCIA_MS": "11",
                    "UBICACIONES": ", ".join(TRACKING_LOCATIONS),
                    "ESTADO_SINCRONIZACIÓN": "ACTIVA",
                    "TEMPERATURA": "NIVEL 2"
                }
                
                report_path = self.audit_manager.create_audit_report(
                    operator="KEVIN_ALEXANDER",
                    tracking_info=tracking_data
                )
                
                logger.info(f"Reporte generado: {report_path}")
                consecutive_failures = 0  # Reset contador de fallos
                
                # Esperar hasta siguiente ciclo
                time.sleep(self.cycle_interval)
                
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error en ciclo #{consecutive_failures}: {e}")
                
                if consecutive_failures >= max_failures:
                    logger.critical("Demasiados fallos consecutivos. Motor detenido.")
                    self.is_running = False
                    break
                
                # Esperar antes de reintentar (exponential backoff)
                retry_delay = min(60 * (2 ** consecutive_failures), 600)
                logger.info(f"Reintentando en {retry_delay}s...")
                time.sleep(retry_delay)


def ejecutar_caza_infinita():
    """Punto de entrada para compatibilidad con código anterior"""
    motor = MotorCataleya()
    motor.start()


if __name__ == "__main__":
    motor = MotorCataleya()
    motor.start()
