import subprocess
import time
from datetime import datetime
import os
import json

# Configuración del Ciclo (60 Minutos por defecto)
INTERVALO_MINUTOS = 60

def mostrar_cabecera():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("============================================================")
    print("         ELITE LA LIGA PREDICTOR: PANEL DE CONTROL          ")
    print("============================================================")
    print(f"  Ultima actualizacion: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("============================================================\n")

def ejecutar_script(nombre_archivo):
    print(f"  [PROCESO] Ejecutando {nombre_archivo}...")
    try:
        # Forzar un entorno con UTF-8 para garantizar estabilidad en Windows
        env_vars = os.environ.copy()
        env_vars["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            ["python", nombre_archivo], 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="replace",
            env=env_vars
        )
        if result.returncode == 0:
            print(f"    [OK] {nombre_archivo} completado.")
            return True
        else:
            print(f"    [ERROR] Error en {nombre_archivo}: {result.stderr}")
            return False
    except Exception as e:
        print(f"    [ERROR] Fallo critico al lanzar {nombre_archivo}: {e}")
        return False

def mostrar_estadisticas():
    print("\n------------------------------------------------------------")
    print("  ESTADO DE LA BASE DE DATOS TACTICA")
    print("------------------------------------------------------------")
    
    # Noticias
    try:
        with open("data/diario_liga.json", "r", encoding="utf-8") as f:
            noticias = json.load(f)
            total_noticias = sum(len(n) for n in noticias.values())
        print(f"  [STAT] Noticias de Prensa: {total_noticias} (Filtradas)")
    except:
        print("  [STAT] Noticias: [Archivo no encontrado]")

    # Alineaciones
    try:
        with open("data/alineaciones_reales.json", "r", encoding="utf-8") as f:
            alineaciones = json.load(f)
            print(f"  [STAT] Alineaciones Reales: {len(alineaciones)}/10")
    except:
        print("  [STAT] Alineaciones: [Archivo no encontrado]")

    # Jornada
    try:
        with open("data/calendario_jornada.json", "r", encoding="utf-8") as f:
            jornada = json.load(f)
            proximos = sum(1 for p in jornada if p["status"] == "Programado")
            print(f"  [STAT] Jornada Activa: {len(jornada)} partidos ({proximos} proximos)")
    except:
        print("  [STAT] Jornada: [Archivo no encontrado]")
    
    print("------------------------------------------------------------\n")

def orquestar_sistema():
    ciclo = 1
    while True:
        mostrar_cabecera()
        print(f"  [LOG] INICIANDO CICLO DE SCOUTING #{ciclo}")
        print("------------------------------------------------------------")
        
        # 1. Sincronizar Calendario (Prioridad 1: Saber qué se juega hoy)
        ejecutar_script("core/creador_de_jornada.py")
        
        # 2. Actualizar Noticias (Prioridad 2: Buscar bajas/sanciones)
        ejecutar_script("core/reportero.py")
        
        # 3. Cazar Alineaciones (Prioridad 3: Ver los onces antes del pitido)
        ejecutar_script("core/cazador_alineaciones.py")
        
        mostrar_estadisticas()
        
        print(f"  [WAIT] Ciclo {ciclo} finalizado. Proxima actualizacion en {INTERVALO_MINUTOS} minutos...")
        print("  (Presiona Ctrl+C para detener el bot)")
        
        ciclo += 1
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    try:
        orquestar_sistema()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Bot detenido por el usuario. Suerte con las apuestas!")
