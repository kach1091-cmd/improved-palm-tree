"""Lock de archivos para sincronización entre threads"""

import threading
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FileLock:
    """Lock por archivo para evitar race conditions"""
    
    _locks = {}  # Dict global de locks por ruta
    _locks_lock = threading.Lock()  # Lock para el dict de locks
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self._acquire_lock()
    
    @classmethod
    def _acquire_lock(cls, filepath: str = None):
        """Obtener o crear un lock para un archivo"""
        if filepath is None:
            return
        
        filepath = str(Path(filepath).absolute())
        
        with cls._locks_lock:
            if filepath not in cls._locks:
                cls._locks[filepath] = threading.RLock()
            return cls._locks[filepath]
    
    def __enter__(self):
        """Adquirir lock al entrar en contexto"""
        filepath = str(self.filepath.absolute())
        self.lock = self._acquire_lock(filepath)
        self.lock.acquire()
        logger.debug(f"Lock adquirido: {self.filepath}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Liberar lock al salir del contexto"""
        self.lock.release()
        logger.debug(f"Lock liberado: {self.filepath}")
        return False
