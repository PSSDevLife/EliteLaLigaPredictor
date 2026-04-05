import pandas as pd
import warnings
import numpy as np

warnings.filterwarnings('ignore')

def compilar_ratios():
    print("=" * 60)
    print("  INICIANDO CEREBRO MATEMATICO (V4) - RATIOS PREDICTIVOS")
    print("=" * 60)
    
    try:
        # 1. Cargar el histórico
        df_hist = pd.read_csv('data/historico_laliga.csv')
        
        # 2. Desglosar Vista Equipo (Local y Vis)
        df_local = df_hist[['Fecha', 'Local', 'Goles_Local', 'Goles_Visitante', 'Tiros_Local', 'Tiros_Visitante', 
                            'TirosPuerta_Local', 'TirosPuerta_Visitante', 'Faltas_Local', 'Faltas_Visitante', 
                            'Corners_Local', 'Corners_Visitante', 'Amarillas_Local', 'Amarillas_Visitante', 
                            'Rojas_Local', 'Rojas_Visitante']].copy()
        df_local['Condicion'] = 'Local'
        df_local.rename(columns={
            'Local': 'Equipo',
            'Goles_Local': 'Goles_Favor', 'Goles_Visitante': 'Goles_Contra',
            'Tiros_Local': 'Tiros_Favor', 'Tiros_Visitante': 'Tiros_Contra',
            'TirosPuerta_Local': 'TirosPuerta_Favor', 'TirosPuerta_Visitante': 'TirosPuerta_Contra',
            'Faltas_Local': 'Faltas_Cometidas', 'Faltas_Visitante': 'Faltas_Recibidas',
            'Corners_Local': 'Corners_Favor', 'Corners_Visitante': 'Corners_Contra',
            'Amarillas_Local': 'Amarillas_Propias', 'Amarillas_Visitante': 'Amarillas_Rivales',
            'Rojas_Local': 'Rojas_Propias', 'Rojas_Visitante': 'Rojas_Rivales'
        }, inplace=True)
        
        df_vis = df_hist[['Fecha', 'Visitante', 'Goles_Visitante', 'Goles_Local', 'Tiros_Visitante', 'Tiros_Local', 
                          'TirosPuerta_Visitante', 'TirosPuerta_Local', 'Faltas_Visitante', 'Faltas_Local', 
                          'Corners_Visitante', 'Corners_Local', 'Amarillas_Visitante', 'Amarillas_Local', 
                          'Rojas_Visitante', 'Rojas_Local']].copy()
        df_vis['Condicion'] = 'Visitante'
        df_vis.rename(columns={
            'Visitante': 'Equipo',
            'Goles_Visitante': 'Goles_Favor', 'Goles_Local': 'Goles_Contra',
            'Tiros_Visitante': 'Tiros_Favor', 'Tiros_Local': 'Tiros_Contra',
            'TirosPuerta_Visitante': 'TirosPuerta_Favor', 'TirosPuerta_Local': 'TirosPuerta_Contra',
            'Faltas_Visitante': 'Faltas_Cometidas', 'Faltas_Local': 'Faltas_Recibidas',
            'Corners_Visitante': 'Corners_Favor', 'Corners_Local': 'Corners_Contra',
            'Amarillas_Visitante': 'Amarillas_Propias', 'Amarillas_Local': 'Amarillas_Rivales',
            'Rojas_Visitante': 'Rojas_Propias', 'Rojas_Local': 'Rojas_Rivales'
        }, inplace=True)
        
        df_unido = pd.concat([df_local, df_vis], ignore_index=True)
        
        # 3. PRE-CÁLCULOS BOOLEANOS (La Magia Matemática)
        # Convertimos condiciones en 1 y 0 para analizarlas con .mean()
        df_unido['Is_Clean_Sheet'] = (df_unido['Goles_Contra'] == 0).astype(int)
        df_unido['Did_Score'] = (df_unido['Goles_Favor'] > 0).astype(int)
        df_unido['Is_Over_2_5'] = ((df_unido['Goles_Favor'] + df_unido['Goles_Contra']) > 2.5).astype(int)

        # 4. Agrupación Base
        agrupado = df_unido.groupby('Equipo').agg(
            Partidos_Jugados=('Fecha', 'count'),
            Goles_Marcados_AVG=('Goles_Favor', 'mean'),
            Goles_Encajados_AVG=('Goles_Contra', 'mean'),
            Tiros_Totales_AVG=('Tiros_Favor', 'mean'),
            Tiros_Contra_AVG=('Tiros_Contra', 'mean'),
            Tiros_Puerta_AVG=('TirosPuerta_Favor', 'mean'),
            Muro_Defensivo_AVG=('TirosPuerta_Contra', 'mean'), 
            Corners_Provocados_AVG=('Corners_Favor', 'mean'),
            Corners_Concedidos_AVG=('Corners_Contra', 'mean'),
            Faltas_Cometidas_AVG=('Faltas_Cometidas', 'mean'),
            Faltas_Recibidas_AVG=('Faltas_Recibidas', 'mean'),
            Amarillas_Propias_AVG=('Amarillas_Propias', 'mean'),
            Amarillas_Rivales_AVG=('Amarillas_Rivales', 'mean'),
            Rojas_Propias_AVG=('Rojas_Propias', 'mean'),
            
            # Agregadores de Probabilidad (se multiplican en bloque)
            Clean_Sheets_Prob=('Is_Clean_Sheet', 'mean'),
            BTTS_Offensive_Prob=('Did_Score', 'mean'),
            Over_2_5_Prob=('Is_Over_2_5', 'mean')
        ).reset_index()
        
        # 5. GENERACIÓN DE RATIOS SINTÉTICOS Y PORCENTAJES DE APUESTA
        
        # Traducir los Probs a Porcentajes % visuales para cuotas
        agrupado['Porteria_a_Cero_%'] = agrupado['Clean_Sheets_Prob'] * 100
        agrupado['Partidos_Anotando_%'] = agrupado['BTTS_Offensive_Prob'] * 100
        agrupado['Over_2.5_Goles_%'] = agrupado['Over_2_5_Prob'] * 100
        
        # Rendimiento de Disparo
        agrupado['Letalidad_Real_%'] = (agrupado['Goles_Marcados_AVG'] / agrupado['Tiros_Puerta_AVG'] * 100).fillna(0)
        agrupado['Punteria_Ofensiva_%'] = (agrupado['Tiros_Puerta_AVG'] / agrupado['Tiros_Totales_AVG'] * 100).fillna(0)
        
        # Índices Secretos
        # Suerte_Defensiva_xGA (Porcentaje de Tiros a Puerta que acaban entrando. Si es MUY bajo, tienen gran Portero/Defensa).
        agrupado['Conversion_Contra_Suerte_%'] = (agrupado['Goles_Encajados_AVG'] / agrupado['Muro_Defensivo_AVG'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        
        # Agresividad y Árbitros
        agrupado['Resistencia_Arbitral_Ratio'] = (agrupado['Faltas_Cometidas_AVG'] / agrupado['Amarillas_Propias_AVG']).replace([np.inf, -np.inf], 0).fillna(0)
        agrupado['Dureza_del_Rival_Ratio'] = (agrupado['Faltas_Recibidas_AVG'] / agrupado['Amarillas_Rivales_AVG']).replace([np.inf, -np.inf], 0).fillna(0)
        
        # Dominio Neto
        agrupado['Dominio_Neto_Tiros'] = agrupado['Tiros_Totales_AVG'] - agrupado['Tiros_Contra_AVG']
        agrupado['Dominio_Neto_Corners'] = agrupado['Corners_Provocados_AVG'] - agrupado['Corners_Concedidos_AVG']

        # Limpiar columnas auxiliares de calc para que no hagan ruido
        agrupado = agrupado.drop(columns=['Clean_Sheets_Prob', 'BTTS_Offensive_Prob', 'Over_2_5_Prob'])
        
        # 6. EXPORTACIÓN
        cols_numericas = agrupado.select_dtypes(include=['float64']).columns
        agrupado[cols_numericas] = agrupado[cols_numericas].round(2)
        
        agrupado['Score'] = agrupado['Goles_Marcados_AVG'] - agrupado['Goles_Encajados_AVG']
        agrupado = agrupado.sort_values(by='Score', ascending=False).drop('Score', axis=1)
        
        output_file = "data/perfiles_equipos_apuestas.csv"
        agrupado.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"[OK] CEREBRO V4: COMPILACION MATEMATICA COMPLETADA.")
        print(f"      -> Creados 20 perfiles súper-masivos con {len(agrupado.columns)} columnas orientadas a Apuestas.")

    except Exception as e:
        print(f"[ERROR] Critico en compilacion algoritmica: {e}")

if __name__ == "__main__":
    compilar_ratios()
