# Práctica de Scraping de comentarios: Extracción de comentarios P.1

Este proyecto de web scraping utiliza `requests` y `BeautifulSoup` para extraer comentarios de una página de peliculas.

## Descripción

El script accede a una URL específica de una noticia en Xataka y extrae información clave:
- **Título del artículo**
- **Contenido del artículo** (en formato texto plano, eliminando ciertos elementos de estilo)
- **Lista de categorías de navegación** (obtenidas de elementos `<li>` específicos)

> **Nota**: Este programa es solo para fines educativos. Asegúrate de cumplir con las políticas de uso y scraping del sitio web.

## Uso

Para ejecutar el script, asegúrate de tener instaladas las bibliotecas requeridas y luego ejecuta el archivo en Python.

### Requisitos

- **Python 3.x**
- **Requests**
- **BeautifulSoup4**

Instala las dependencias ejecutando:

```bash
pip install requests beautifulsoup4
```

## ⚙️ Instalación
Clonar el repositorio:

```bash
git clone https://github.com/G1okz/webScraping.git

