import time
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Setup logging with rotation
log_dir = Path("INFORMES_AUDITORIA")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("auditoria")
logger.setLevel(logging.INFO)

# Rotating file handler - max 5 files of 10MB each
handler = RotatingFileHandler(
    log_dir / "auditoria.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def generar_informe(timestamp):
    """Generate audit report with proper buffering"""
    try:
        informe_path = log_dir / f"AUDITORIA_{timestamp}.md"
        
        # Buffer content instead of multiple writes
        content = [
            f"# INFORME DE MISIÓN OMEGA - {timestamp}\n",
            "OPERADOR: KEVIN ALEXANDER | MODO: INFINITO\n",
            "LATENCIA: 11ms | TEMPERATURA: NIVEL 2\n",
            "-" * 100 + "\n",
            "RASTREO: Dubái Root, Swiss Vault, London Exchange.\n",
            "ESTADO: Bulla generada. Sensores de inversión buscando comprador.\n",
            "CONGRUENCIA: Sincronía total entre Catalina y el Clon.\n"
        ]
        
        # Single write operation
        with open(informe_path, "w") as f:
            f.writelines(content)
        
        return True
    except IOError as e:
        logger.error(f"Error escribiendo informe: {e}")
        return False

def ejecutar_auditoria(running=None):
    """
    Run audit with graceful shutdown support
    
    Args:
        running: Optional callable/object with running state
    """
    logger.info("MOTORES A 100%: DESPEGUE HACIA LA RAÍZ (11ms)")
    print("\n[!] MOTORES A 100%: DESPEGUE HACIA LA RAÍZ (11ms)")
    
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
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            
            # Generate report
            if generar_informe(timestamp):
                logger.info(f"Auditoría generada y sellada: {timestamp}")
                print(f"[V] Auditoría generada y sellada: {timestamp} (Ciclo: {ciclos})")
            
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
        logger.info("Auditoría interrumpida por usuario")
        print("\n[!] Auditoría interrumpida")
    except Exception as e:
        logger.error(f"Error en auditoría: {e}")
        print(f"[ERROR] {e}")
    finally:
        logger.info(f"Auditoría finalizada. Total ciclos: {ciclos}")
        print(f"[!] Auditoría finalizada. Total ciclos: {ciclos}")

if __name__ == "__main__":
    ejecutar_auditoria()
