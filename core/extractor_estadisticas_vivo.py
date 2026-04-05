import pandas as pd
import requests
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore') # Ocultar alertas de pandas temporales

def mapear_equipo(nombre):
    """Convierte los nombres de ESPN a la estructura clásica de Football-Data."""
    n = str(nombre).lower()
    if 'atlético' in n or 'atl madrid' in n: return 'Ath Madrid'
    if 'athletic' in n or 'bilbao' in n: return 'Ath Bilbao'
    if 'sociedad' in n: return 'Sociedad'
    if 'betis' in n: return 'Betis'
    if 'rayo' in n or 'vallecano' in n: return 'Vallecano'
    if 'barcelona' in n: return 'Barcelona'
    if 'espanyol' in n or 'español' in n: return 'Espanol'
    if 'alav' in n: return 'Alaves'
    if 'osasuna' in n: return 'Osasuna'
    if 'mallorca' in n: return 'Mallorca'
    if 'getafe' in n: return 'Getafe'
    if 'valencia' in n: return 'Valencia'
    if 'levante' in n: return 'Levante'
    if 'elche' in n: return 'Elche'
    if 'celta' in n: return 'Celta'
    if 'girona' in n: return 'Girona'
    if 'oviedo' in n: return 'Oviedo'
    if 'villarreal' in n: return 'Villarreal'
    if 'sevilla' in n: return 'Sevilla'
    if 'real madrid' in n: return 'Real Madrid'
    if 'palmas' in n: return 'Las Palmas'
    if 'legan' in n: return 'Leganes'
    if 'valladolid' in n: return 'Valladolid'
    return nombre

def obtener_temporada_actual_str():
    hoy = datetime.today()
    if hoy.month < 8:
        año_inicio = hoy.year - 1
        año_fin = hoy.year
    else:
        año_inicio = hoy.year
        año_fin = hoy.year + 1
    return f"{año_inicio % 100:02d}{año_fin % 100:02d}"

def descargar_base_masiva():
    """Descarga el bloque principal de datos históricos."""
    temporada_str = obtener_temporada_actual_str()
    url = f"https://www.football-data.co.uk/mmz4281/{temporada_str}/SP1.csv"
    print(f"[*] Obteniendo Base Masiva (Football-Data): {url}")
    
    try:
        df = pd.read_csv(url)
        columnas_mantener = [
            'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 
            'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 
            'HC', 'AC', 'HY', 'AY', 'HR', 'AR'
        ]
        columnas_validas = [col for col in columnas_mantener if col in df.columns]
        df = df[columnas_validas].copy()
        
        nombres_espanol = {
            'Date': 'Fecha', 'HomeTeam': 'Local', 'AwayTeam': 'Visitante',
            'FTHG': 'Goles_Local', 'FTAG': 'Goles_Visitante',
            'HS': 'Tiros_Local', 'AS': 'Tiros_Visitante',
            'HST': 'TirosPuerta_Local', 'AST': 'TirosPuerta_Visitante',
            'HF': 'Faltas_Local', 'AF': 'Faltas_Visitante',
            'HC': 'Corners_Local', 'AC': 'Corners_Visitante',
            'HY': 'Amarillas_Local', 'AY': 'Amarillas_Visitante',
            'HR': 'Rojas_Local', 'AR': 'Rojas_Visitante'
        }
        df.rename(columns=nombres_espanol, inplace=True)
        return df
    except Exception as e:
        print(f"[ERROR] Bloque Masivo falló: {e}")
        return pd.DataFrame()

def obtener_stats_directo_espn(match_id):
    """Extrae tarjetas, corners, tiros y faltas haciendo ping directo al BoxScore de ESPN."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/summary?event={match_id}"
    try:
        res = requests.get(url, timeout=10).json()
        equipos = res.get('boxscore', {}).get('teams', [])
        
        stat_dict = {}
        for equipo in equipos:
            home_away = equipo.get('homeAway')
            stats_crudas = equipo.get('statistics', [])
            stats = {s.get('name'): str(s.get('displayValue')) for s in stats_crudas}
            
            # Helper to parse ESPN strings which might rarely be weird or decimals
            def parse_stat(val_str):
                try: return int(float(val_str))
                except: return 0
                
            prefix = "Local" if home_away == "home" else "Visitante"
            stat_dict[f'Corners_{prefix}'] = parse_stat(stats.get('wonCorners', '0'))
            stat_dict[f'Amarillas_{prefix}'] = parse_stat(stats.get('yellowCards', '0'))
            stat_dict[f'Rojas_{prefix}'] = parse_stat(stats.get('redCards', '0'))
            stat_dict[f'Tiros_{prefix}'] = parse_stat(stats.get('totalShots', '0'))
            stat_dict[f'TirosPuerta_{prefix}'] = parse_stat(stats.get('shotsOnTarget', '0'))
            stat_dict[f'Faltas_{prefix}'] = parse_stat(stats.get('foulsCommitted', '0'))

        return stat_dict
    except Exception as e:
        return {}

def cazar_partidos_recientes_espn(df_base):
    """Caza partidos terminados recientement para rellenar los huecos que no tiene la BD masiva."""
    print("[*] Lanzando Radar ESPN (Ultimos 7 dias)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    fechas_str = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
    
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard?dates={fechas_str}"
    
    try:
        res = requests.get(url, timeout=10).json()
        eventos = res.get('events', [])
        
        añadidos = 0
        nuevas_filas = []
        
        for evento in eventos:
            estado = evento.get('status', {}).get('type', {}).get('state')
            if estado == 'post':  # Finalizado
                match_id = evento['id']
                fecha_iso = evento['date']
                fecha_obj = datetime.strptime(fecha_iso[:10], "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                
                competidores = evento.get('competitions', [])[0].get('competitors', [])
                equipo_local_obj = next((c for c in competidores if c['homeAway'] == 'home'), {})
                equipo_vis_obj = next((c for c in competidores if c['homeAway'] == 'away'), {})
                
                local = mapear_equipo(equipo_local_obj.get('team', {}).get('displayName', ''))
                visitante = mapear_equipo(equipo_vis_obj.get('team', {}).get('displayName', ''))
                
                goles_local = equipo_local_obj.get('score', '0')
                goles_vis = equipo_vis_obj.get('score', '0')
                
                ya_existe = not df_base[
                    (df_base['Local'].str.contains(local[:5], case=False, na=False)) & 
                    (df_base['Visitante'].str.contains(visitante[:5], case=False, na=False))
                ].empty
                
                if not ya_existe:
                    stats_completas = obtener_stats_directo_espn(match_id)
                    
                    fila = {
                        'Fecha': fecha_formateada,
                        'Local': local,
                        'Visitante': visitante,
                        'Goles_Local': goles_local,
                        'Goles_Visitante': goles_vis,
                        'Tiros_Local': stats_completas.get('Tiros_Local', 0),
                        'Tiros_Visitante': stats_completas.get('Tiros_Visitante', 0),
                        'TirosPuerta_Local': stats_completas.get('TirosPuerta_Local', 0),
                        'TirosPuerta_Visitante': stats_completas.get('TirosPuerta_Visitante', 0),
                        'Faltas_Local': stats_completas.get('Faltas_Local', 0),
                        'Faltas_Visitante': stats_completas.get('Faltas_Visitante', 0),
                        'Corners_Local': stats_completas.get('Corners_Local', 0),
                        'Corners_Visitante': stats_completas.get('Corners_Visitante', 0),
                        'Amarillas_Local': stats_completas.get('Amarillas_Local', 0),
                        'Amarillas_Visitante': stats_completas.get('Amarillas_Visitante', 0),
                        'Rojas_Local': stats_completas.get('Rojas_Local', 0),
                        'Rojas_Visitante': stats_completas.get('Rojas_Visitante', 0)
                    }
                    nuevas_filas.append(fila)
                    añadidos += 1
                    print(f"    [+] {local} vs {visitante} (Fresco desde ESPN) INYECTADO con estadisticas profundas.")
        
        if nuevas_filas:
            df_nuevas = pd.DataFrame(nuevas_filas)
            df_final = pd.concat([df_base, df_nuevas], ignore_index=True)
            return df_final, añadidos
        else:
            print("    [-] El historial masivo ya estaba al dia. Ningun partido nuevo inyectado.")
            return df_base, 0

    except Exception as e:
        print(f"[ERROR] Radar ESPN fallo: {e}")
        return df_base, 0

def calcular_jornadas_guardar(df):
    """Calcula las jornadas matemáticamente y guarda la obra maestra."""
    conteo_partidos = {}
    jornadas = []
    
    for index, row in df.iterrows():
        local = row['Local']
        visitante = row['Visitante']
        j_local = conteo_partidos.get(local, 0) + 1
        j_vis = conteo_partidos.get(visitante, 0) + 1
        jornada_actual = max(j_local, j_vis)
        jornadas.append(f"J{jornada_actual}")
        conteo_partidos[local] = j_local
        conteo_partidos[visitante] = j_vis
        
    df.insert(0, 'Jornada', jornadas)
    
    output_file = "data/historico_laliga.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n[OK] HISTORICO HIBRIDO GENERADO: {output_file} ({len(df)} partidos, {len(df.columns)} columnas metricas).")

if __name__ == "__main__":
    print("=" * 60)
    print("  INICIANDO EXTRACTOR HIBRIDO DE ALTA PROFUNDIDAD")
    print("=" * 60)
    
    df_base = descargar_base_masiva()
    if not df_base.empty:
        df_completo, inyectados = cazar_partidos_recientes_espn(df_base)
        calcular_jornadas_guardar(df_completo)
    else:
        print("[ERROR] No se pudo iniciar el proceso debido al fallo de la base masiva.")
