# 🏆 Élite LaLiga Predictor (Automated Betting Bot)

Bienvenido a la Arquitectura Central de Inteligencia del Bot de Apuestas. Este repositorio de código es un ecosistema 100% autónomo diseñado para recolectar, sanear y perfilar matemáticamente datos ofensivos, defensivos y de contexto en tiempo real para generar apuestas rentables en la liga española de fútbol (La Liga).

El proyecto funciona recolectando sin supervisión noticias (lesiones), onces titulares, y las métricas crudas de todos los partidos para compilar en un perfil cuánta "Letalidad" y "Agresividad Arbitral" tiene cada equipo a ojos de una Inteligencia Artificial.

---

## 📂 Organización de Carpetas

La arquitectura del bot está separada profesionalmente en responsabilidades modulares:

*   **`core/`**: Los Motores. Aquí es donde habitan todos los módulos ("cerebros") que trabajan de forma automática consiguiendo información desde rincones ocultos de la web.
*   **`data/`**: La Bóveda Intocable. Archivos JSON y CSV generados por los módulos `core`. Es el alimento del futuro Bot Predictivo de Telegram.
*   **`docs/`**: Textos explicativos sobre qué significa cada métrica u algoritmos de la IA para un humano.

---

## ⚙️ 1. ARCHIVOS "CORE/" (La Maquinaria)

Cada uno de estos scripts python tiene una misión específica y es convocado por el Orquestador central.

### 📰 `reportero.py`
Se conecta a unos 40 canales RSS ocultos de Marca y de As cada hora. Descarta las noticias del corazón e inserta una etiqueta de alerta `[SANCION]` autómaticamente en el texto si la noticia menciona una lesión en la pierna o un castigo con tarjetas para darnos contexto vital antes del fin de semana. Además purga (borra) toda noticia que tenga más de 48 horas de antigüedad él solito.

### 📅 `creador_de_jornada.py`
Es el "sincronizador" del tiempo. Va a las bases oficiales y averigua exactamente qué número de Jornada toca jugar este fin de semana, devolviendo el calendario con las horas de cada partido y sus Ids Oficiales para que el resto del bot no se pierda. 

### 👕 `cazador_alineaciones.py`
Es un francotirador de última hora. Revisa la base de la jornada y, si ve que un partido se juega hoy mismo, escanea las APIs deportivas para ver si existen las alineaciones confirmadas. Si el 11 inicial está subido, lo guarda.

### 📊 `extractor_estadisticas_vivo.py` (Histórico V2)
Es el Motor Híbrido de Datos Masivos. Descarga la estadística de toda la temporada (más de 300 partidos) a través de una base de datos británica (Football-Data) y la fusiona EN VIVO interactuando con la API secreta de ESPN para absorber los partidos que acaban de terminar unos minutos atrás. Recoge Goles, Tarjetas Rojas/Amarillas, Córners y los super datos de Faltas Cometidas y Tiros Totales y a Puerta de cada equipo.

### 🧮 `compilador_ratios_equipos.py` (Cerebro Matemático V4)
Es la Calculadora de las Casas de Apuestas. En lugar de procesar los datos a lo loco, se encarga de despivotar el archivo general histórico para compilarlo todo por equipos. Por cada equipo cruza los números del extractor y genera 25 súper columnas. Extrae los % de Probabilidad pura ("Portería a Cero", "Partidos Over 2.5", "Marca Gol") y genera índices cruzados como su "Rendimiento Defensivo / Suerte" o la "Puntería de cara a Puerta".

---

## 💾 2. ARCHIVOS "DATA/" (La Base de Datos Extraída)

El trabajo duro del punto anterior escupe todo este arsenal analítico limpio en esta carpeta listos para abrirse de una tacada:

*   **`diario_liga.json`**: El periódico en vivo expurgado (noticias puras del fútbol de las ult. 48h).
*   **`alineaciones_reales.json`**: Quién va a jugar hoy titular (vital por si se cae el delantero estrella).
*   **`calendario_jornada.json`**: El mapamundi temporal del fin de semana.
*   **`historico_laliga.csv`**: Un CSV gigantesco y ordenado con todos los Córners, Faltas y Tiros de todos los partidos pasados.
*   **`perfiles_equipos_apuestas.csv`**: El escáner métrico puro (una lista cerrada de los 20 equipos analizados y punteados mediante algoritmos ofensivos).

---

## 🚀 3. EL GRAN ORQUESTADOR MÁGICO

### 🟢 `sistema_control.py`
Este archivo es el **Orquestador Maestro** y el corazón de tu Ecosistema Inteligente.

**¿El flujo de trabajo actual?**  
Si lanzamos `sistema_control.py`, enciende automáticamente TODA la batería de módulos de forma programática. En un solo ciclo: (1) Sincronizará la Jornada, (2) Extraerá el parte de Sanciones, (3) Cazará alineaciones en vivo, (4) Engordará el archivo histórico interceptando saques de esquina a nivel informático en ESPN y (5) Engranará la matemática fabricándote los Perfiles de Rentabilidad de Apuestas V4. Todo en cadena, repitiéndolo incansablemente cada 60 minutos y con una interfaz limpia que asoma el conteo verde en tu propia pantalla. Operacional "Set-and-Forget".
