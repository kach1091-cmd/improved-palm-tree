#!/bin/bash
# escudo_fantasma.sh - Pulsación de defensa con límite de iteraciones

set -euo pipefail

HEARTBEAT_INTERVAL=60
MAX_ITERATIONS=1440  # 24 horas si interval=60s
COUNTER=0
LOG_FILE="logs/escudo_fantasma.log"

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Trap para capturar señales de terminación
trap 'echo "[$(date +'%Y-%m-%d %H:%M:%S')] Escudo fantasma detenido" | tee -a "$LOG_FILE"; exit 0' SIGTERM SIGINT

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Escudo fantasma activado - Máximo de ciclos: $MAX_ITERATIONS" | tee -a "$LOG_FILE"

while [[ $COUNTER -lt $MAX_ITERATIONS ]]; do
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Sincronía 5234: Pulsación de defensa activa..." | tee -a "$LOG_FILE"
    ((COUNTER++))
    sleep "$HEARTBEAT_INTERVAL"
done

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Escudo fantasma completado - $COUNTER ciclos ejecutados" | tee -a "$LOG_FILE"
exit 0
