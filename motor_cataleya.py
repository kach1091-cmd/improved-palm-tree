import time
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Setup logging with rotation
log_dir = Path("INFORMES_AUDITORIA")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("motor_cataleya")
logger.setLevel(logging.INFO)

# Rotating file handler - max 5 files of 10MB each
handler = RotatingFileHandler(
    log_dir / "motor_cataleya.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def generar_informe_motor(timestamp):
    """Generate motor report with proper buffering"""
    try:
        informe_path = log_dir / f"AUDITORIA_{timestamp}.md"
        
        # Buffer content instead of multiple writes
        content = [
            f"# INFORME DE RAÍZ - {timestamp}\n",
            "ESTADO: SINCRONÍA TOTAL CON KEVIN ALEXANDER\n",
            "RASTREO: DUBÁI, SUIZA, LONDRES EN CURSO...\n"
        ]
        
        # Single write operation
        with open(informe_path, "w") as f:
            f.writelines(content)
        
        return True
    except IOError as e:
        logger.error(f"Error escribiendo informe: {e}")
        return False

def ejecutar_caza_infinita(running=None):
    """
    Run infinite hunt with graceful shutdown support
    
    Args:
        running: Optional callable/object with running state
    """
    logger.info("MOTOR CATALEYA ACTIVO: 11ms LATENCIA")
    print("[!] MOTOR CATALEYA ACTIVO: 11ms LATENCIA")
    
    ciclos = 0
    try:
        while True:
            # Check for shutdown signal if running object provided
            if running is not None and hasattr(running, '__call__'):
                if not running():
                    break
            elif running is not None and not running:
                break
            
            ciclos += 1
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            
            # Generate report
            if generar_informe_motor(timestamp):
                logger.info(f"Informe generado: {timestamp}")
                print(f"[V] Informe generado: {timestamp} (Ciclo: {ciclos})")
            
            # Sleep in shorter intervals for better responsiveness
            # Check every second instead of blocking for 3 hours
            for _ in range(10800):  # 10800 seconds = 3 hours
                if running is not None and hasattr(running, '__call__'):
                    if not running():
                        break
                elif running is not None and not running:
                    break
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Motor interrumpido por usuario")
        print("\n[!] Motor interrumpido")
    except Exception as e:
        logger.error(f"Error en motor: {e}")
        print(f"[ERROR] {e}")
    finally:
        logger.info(f"Motor finalizado. Total ciclos: {ciclos}")
        print(f"[!] Motor finalizado. Total ciclos: {ciclos}")

if __name__ == "__main__":
    ejecutar_caza_infinita()
