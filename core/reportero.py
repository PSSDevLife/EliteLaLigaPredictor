import feedparser
import json
import re
from datetime import datetime, timedelta

# --- CONFIGURACION DE ELITE ---
CATEGORIAS_A_FILTRAR = [
    "sub-12", "sub12", "fc futures", "mundialito", "brunete",
    "en imagenes", "las fotos", "galería", "fotogalería", "fotos de",
    "video", "pódcast", "directo", "horario", "televisión", "dónde ver",
    "redes sociales", "twitter", "instagram", "tiktok", "viral",
    "pareja de", "novia de", "mujer de", "famoso", "corazón"
]

MAPA_EQUIPOS_RSS = {
    "Alaves": ["alaves", "mendi", "babazorros"],
    "Athletic": ["athletic", "san mames", "leones"],
    "Atletico": ["atletico", "metropolitano", "simeone", "colchoneros"],
    "Barcelona": ["barcelona", "fc barcelona", "barça", "blaugranas", "cules", "camp nou"],
    "Betis": ["betis", "villamarin", "heliopolis", "verdiblancos"],
    "Celta": ["celta", "balaidos", "olvicos"],
    "Elche": ["elche", "ilicitanos", "martinez valero"],
    "Espanyol": ["espanyol", "pericos", "rcde", "cornella"],
    "Getafe": ["getafe", "azulones", "coliseum", "bordalas"],
    "Girona": ["girona", "gironins", "montilivi", "michel"],
    "Levante": ["levante", "granotas", "ciutat de valencia"],
    "Mallorca": ["mallorca", "son moix", "bermejones"],
    "Osasuna": ["osasuna", "el sadar", "rojillos"],
    "Rayo": ["rayo", "vallecas", "franjirrojos"],
    "Real Madrid": ["real madrid", "bernabeu", "blancos", "merengues", "ancelotti"],
    "Real Oviedo": ["oviedo", "tartiere", "carbayones"],
    "Real Sociedad": ["real sociedad", "anoeta", "txuri-urdin"],
    "Sevilla": ["sevilla", "nervion", "sanchez-pizjuan"],
    "Valencia": ["valencia", "mestalla", "ches"],
    "Villarreal": ["villarreal", "submarino amarillo", "ceramica", "marcelino"]
}

# --- NUEVAS URLS DE ALTO RENDIMIENTO (MARCA Y AS) ---
def actualizar_diario():
    print(f"[{datetime.now().strftime('%H:%M')}] [RSS] Iniciando Escaneo de Prensa con Canales Actualizados...")
    
    try:
        with open("data/diario_liga.json", "r", encoding="utf-8") as f:
            noticias_por_equipo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        noticias_por_equipo = {equipo: [] for equipo in MAPA_EQUIPOS_RSS}

    links_procesados = set()
    for lista in noticias_por_equipo.values():
        for n in lista:
            links_procesados.add(n["link"])

    sanciones_cont = 0
    filtradas_cont = 0
    
    # Canales Generales y Específicos de Marca (Nuevo dominio objetos.estaticos-marca.com)
    feeds_objetivo = [
        ("Marca Gral", "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml"),
        ("AS Gral", "https://feeds.as.com/mrss-s/pages/as/site/as.com/section/futbol/subsection/primera/")
    ]
    
    # Añadimos canales por equipo de Marca (Los más fiables)
    for eq_slug in MAPA_EQUIPOS_RSS:
        slug = eq_slug.lower().replace(" ", "-")
        feeds_objetivo.append(("Marca", f"https://objetos.estaticos-marca.com/rss/futbol/{slug}.xml"))

    for fuente_nombre, url_rss in feeds_objetivo:
        print(f">> Analizando Canal: {fuente_nombre} ({url_rss[:40]}...)", end="\r")
        feed = feedparser.parse(url_rss)
        
        for entry in feed.entries:
            titulo = entry.get("title", "")
            link = entry.get("link", "")
            desc = entry.get("description", "")
            
            if link in links_procesados:
                continue
            
            if filtrar_basura(titulo, desc):
                filtradas_cont += 1
                continue
            
            # DETECTOR DE SANCIONES
            tag_sancion = ""
            if es_sancion(titulo, desc):
                tag_sancion = "[SANCION] "
                sanciones_cont += 1
            
            equipos_implicados = obtener_equipos_mencionados(titulo, link, desc)
            
            # Si es un canal de equipo de Marca, ya sabemos a quién va dirigido
            if fuente_nombre == "Marca" and not equipos_implicados:
                # Extraer el slug de la URL para saber de qué equipo es
                for eq_key in MAPA_EQUIPOS_RSS:
                    if eq_key.lower().replace(" ", "-") in url_rss:
                        equipos_implicados = [eq_key]
                        break

            if not equipos_implicados:
                continue

            noticia_obj = {
                "titulo": tag_sancion + titulo,
                "fuente": fuente_nombre,
                "link": link,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            for eq in equipos_implicados:
                if eq in noticias_por_equipo:
                    noticias_por_equipo[eq].append(noticia_obj)
            
            links_procesados.add(link)

    # Limpieza de noticias viejas (> 48h)
    limite = datetime.now() - timedelta(hours=48)
    for eq in noticias_por_equipo:
        noticias_por_equipo[eq] = [
            n for n in noticias_por_equipo[eq] 
            if datetime.strptime(n["fecha"], "%Y-%m-%d %H:%M") > limite
        ]

    with open("data/diario_liga.json", "w", encoding="utf-8") as f:
        json.dump(noticias_por_equipo, f, indent=4, ensure_ascii=False)
    
    total = sum(len(v) for v in noticias_por_equipo.values())
    print(f"\n[OK] Inteligencia Profunda finalizada. {total} noticias capturadas.")
    print(f">> Se han detectado {sanciones_cont} posibles sanciones.")
    print(f">> Se han descartado {filtradas_cont} noticias irrelevantes/antiguas.")

def es_sancion(titulo, desc):
    palabras_clave = ["sancionado", "sancion", "roja", "cinco amarillas", "ciclo", "comite", "competicion"]
    texto = (titulo + " " + desc).lower()
    return any(p in texto for p in palabras_clave)

def filtrar_basura(titulo, desc):
    texto = (titulo + " " + desc).lower()
    return any(p in texto for p in CATEGORIAS_A_FILTRAR)

def obtener_equipos_mencionados(titulo, link, desc):
    menciones = []
    texto = (titulo + " " + desc + " " + link).lower()
    for equipo, aliases in MAPA_EQUIPOS_RSS.items():
        if any(alias in texto for alias in aliases + [equipo.lower()]):
            menciones.append(equipo)
    return list(set(menciones))

if __name__ == "__main__":
    actualizar_diario()
