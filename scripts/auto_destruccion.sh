#!/bin/bash
# auto_destruccion.sh - Eliminación segura de trazas con manejo de errores

set -euo pipefail

LOG_FILE="security_trace.log"
LOG_DIR="logs"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Iniciando destrucción segura de trazas..." | tee -a "$LOG_DIR/destruction.log"

if [[ -f "$LOG_FILE" ]]; then
    if command -v shred &> /dev/null; then
        if shred -vfz -n 3 "$LOG_FILE" 2>/dev/null; then
            echo "[OK] Archivo $LOG_FILE destruido de forma segura (3 pasadas)" | tee -a "$LOG_DIR/destruction.log"
            exit 0
        else
            echo "[WARN] shred falló, usando rm estándar" | tee -a "$LOG_DIR/destruction.log"
        fi
    fi
    
    # Fallback si shred no está disponible
    if rm -f "$LOG_FILE" 2>/dev/null; then
        echo "[OK] Archivo $LOG_FILE eliminado" | tee -a "$LOG_DIR/destruction.log"
        exit 0
    else
        echo "[ERROR] No se pudo eliminar $LOG_FILE" | tee -a "$LOG_DIR/destruction.log"
        exit 1
    fi
else
    echo "[WARN] Archivo $LOG_FILE no encontrado" | tee -a "$LOG_DIR/destruction.log"
    exit 0
fi
