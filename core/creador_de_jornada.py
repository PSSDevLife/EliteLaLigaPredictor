import requests
import json
from datetime import datetime, timedelta

# Configuración de Identidad (Anti-bloqueo para APIs de Marca)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Referer': 'https://www.marca.com/'
}

# Mapa de Nombres de API -> Nuestra ID de Equipo
# La API usa fullNames y commonNames muy consistentes
MAPA_EQUIPOS_API = {
    "Alavés": "Alaves",
    "Athletic": "Athletic",
    "Atlético de Madrid": "Atletico",
    "Atlético": "Atletico",
    "Barcelona": "Barcelona",
    "Betis": "Betis",
    "Celta": "Celta",
    "Elche": "Elche",
    "Espanyol": "Espanyol",
    "Getafe": "Getafe",
    "Girona": "Girona",
    "Levante": "Levante",
    "Mallorca": "Mallorca",
    "Osasuna": "Osasuna",
    "Rayo": "Rayo",
    "Real Madrid": "Real Madrid",
    "Oviedo": "Real Oviedo",
    "Real Oviedo": "Real Oviedo",
    "Real Sociedad": "Real Sociedad",
    "Sevilla": "Sevilla",
    "Valencia": "Valencia",
    "Villarreal": "Villarreal"
}

def normalizar_equipo(nombre):
    return MAPA_EQUIPOS_API.get(nombre, nombre)

def sincronizar_por_api():
    ahora = datetime.now()
    # Scaneamos un rango más amplio (3 días atrás y 2 adelante) para capturar la Jornada completa
    fechas_a_escaneat = [
        (ahora - timedelta(days=3)).strftime("%Y-%m-%d"),
        (ahora - timedelta(days=2)).strftime("%Y-%m-%d"),
        (ahora - timedelta(days=1)).strftime("%Y-%m-%d"),
        ahora.strftime("%Y-%m-%d"),
        (ahora + timedelta(days=1)).strftime("%Y-%m-%d"),
        (ahora + timedelta(days=2)).strftime("%Y-%m-%d")
    ]
    
    print(f"[{ahora.strftime('%H:%M')}] --- Sincronizacion PROFESIONAL via API ---")
    
    calendario_final = []
    ids_vistos = set()

    for fecha in fechas_a_escaneat:
        url = f"https://api.unidadeditorial.es/sports/v1/events/preset/1_99a16e5b?timezoneOffset=2&date={fecha}"
        print(f"  > Consultando fecha: {fecha}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            eventos = data.get("data", [])
            for evento in eventos:
                # Filtrar por competición (0101 = LaLiga EA Sports)
                if evento.get("tournament", {}).get("id") != "0101":
                    continue
                
                match_id = evento.get("id")
                if match_id in ids_vistos:
                    continue
                
                comp = evento.get("sportEvent", {}).get("competitors", {})
                local_raw = comp.get("homeTeam", {}).get("fullName")
                visitante_raw = comp.get("awayTeam", {}).get("fullName")
                
                local = normalizar_equipo(local_raw)
                visitante = normalizar_equipo(visitante_raw)
                
                # Estado y Resultado
                status_raw = evento.get("status", {}).get("name")
                # Mapeo de estados: 'Finalizado', 'Programado', 'En juego'
                status_final = "Programado"
                if status_raw == "Finalizado":
                    status_final = "Finalizado"
                elif status_raw == "En juego":
                    status_final = "En juego"
                
                resultado = ""
                if status_final == "Finalizado":
                    res = evento.get("score")
                    if res:
                        resultado = f"{res.get('home')}-{res.get('away')}"

                p_data = {
                    "match_id": match_id,
                    "jornada": evento.get("matchDay", "30"),
                    "local": local,
                    "visitante": visitante,
                    "resultado": resultado,
                    "kickoff_time": evento.get("startDate"),
                    "status": status_final,
                    "directo_url": f"https://www.marca.com/eventos/directo/index.html?e={match_id}"
                }
                
                calendario_final.append(p_data)
                ids_vistos.add(match_id)
                print(f"    - [{status_final}] {local} vs {visitante} -> ID: {match_id}")

        except Exception as e:
            print(f"    [ERROR] Error en fecha {fecha}: {e}")

    # Guardar resultados
    if calendario_final:
        with open("data/calendario_jornada.json", "w", encoding="utf-8") as f:
            json.dump(calendario_final, f, indent=4, ensure_ascii=False)
        print(f"[OK] Sincronizacion Elite completada: {len(calendario_final)} partidos guardados.")
    else:
        print("[ERROR] No se encontraron partidos de LaLiga en estas fechas.")

if __name__ == "__main__":
    sincronizar_por_api()
