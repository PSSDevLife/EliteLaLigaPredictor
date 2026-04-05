import requests
import json
from datetime import datetime

# Configuración de Identidad (Anti-bloqueo para APIs de Marca)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Referer': 'https://www.marca.com/'
}

def cazar_alineaciones_elite():
    print(f"[{datetime.now().strftime('%H:%M')}] [HUNTER] Iniciando Caza Elite de Alineaciones...")
    
    try:
        # 1. Cargar el calendario actualizado con Match IDs
        with open("data/calendario_jornada.json", "r", encoding="utf-8") as f:
            partidos = json.load(f)
            
        # 2. Cargar o inicializar base de datos de alineaciones
        try:
            with open("data/alineaciones_reales.json", "r", encoding="utf-8") as f:
                alineaciones_db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            alineaciones_db = {}

        # 3. Escanear cada partido
        partidos_con_once = 0
        for p in partidos:
            match_id = p["match_id"]
            local = p["local"]
            visitante = p["visitante"]
            
            # Solo escaneamos si el partido está programado o para actualizar los ya jugados
            print(f"  🏟️ Analizando {local} vs {visitante} (ID: {match_id})...")
            
            url_api = f"https://api.unidadeditorial.es/sports/v1/events/{match_id}/full?site=2"
            
            try:
                response = requests.get(url_api, headers=HEADERS, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Navegar por el JSON hasta las alineaciones
                # Ruta: data > lineup > lineups > [homeTeam/awayTeam] > inicialLineup
                lineup_data = data.get("data", {}).get("lineup", {}).get("lineups", {})
                
                if not lineup_data:
                    print(f"    ⏳ Alineación aún no disponible en la API.")
                    continue
                
                home_raw = lineup_data.get("homeTeam", {}).get("inicialLineup", [])
                away_raw = lineup_data.get("awayTeam", {}).get("inicialLineup", [])
                
                # Extraer solo los nombres si hay al menos 11 por equipo
                if len(home_raw) >= 11 and len(away_raw) >= 11:
                    titulares_local = [jugador.get("name") for jugador in home_raw]
                    titulares_visitante = [jugador.get("name") for jugador in away_raw]
                    
                    alineaciones_db[match_id] = {
                        "local": local,
                        "visitante": visitante,
                        "once_local": titulares_local,
                        "once_visitante": titulares_visitante,
                        "capturado_at": datetime.now().isoformat()
                    }
                    partidos_con_once += 1
                    print(f"    [OK] ONCE CONFIRMADO capturado.")
                else:
                    print(f"    [WAIT] Alineaciones aun no disponibles.")

            except Exception as e:
                print(f"    Error consultando API para {local}-{visitante}: {e}")

        # 4. Guardar base de datos
        with open("data/alineaciones_reales.json", "w", encoding="utf-8") as f:
            json.dump(alineaciones_db, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Caza Élite finalizada. {partidos_con_once} alineaciones nuevas capturadas.")

    except Exception as e:
        print(f"❌ Error crítico en el Cazador Élite: {e}")

if __name__ == "__main__":
    cazar_alineaciones_elite()
