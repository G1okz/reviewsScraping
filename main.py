import os
import csv
import requests
from bs4 import BeautifulSoup
import re

"""
    @Description: Este script realiza el scraping de comentarios y puntuaciones de películas de Filmaffinity.
        Para cancelar la ejecución del script, presiona Ctrl+C en la terminal.
        
    @Details: El archivo CSV 'movies.csv' contiene los datos de las películas, incluyendo el título, enlace, ID, año y enlace de la portada.
        El archivo CSV 'reviews.csv' contiene los comentarios y puntuaciones de las películas, con las columnas ID, Comentario y Puntuación.
        
    @Important: Este script está diseñado para fines educativos y de aprendizaje.
    
    @Date: 2021-09-29        
    @Author: Miguel Reyna
"""
def get_all_reviews(movie_id):
    page_number = 1
    all_reviews = []
    
    while True:
        reviews_url = f'https://www.filmaffinity.com/es/reviews/{page_number}/{movie_id}.html'
        
        try:
            response = requests.get(reviews_url)
            if response.status_code == 429:
                print(f'Error 429: Too Many Requests for page {page_number} of movie ID {movie_id}. Skipping to next page.')
                page_number += 1
                continue
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            review_texts = soup.find_all('div', class_='review-text1')
            review_ratings = soup.find_all('div', class_='user-reviews-movie-rating')
            
            if review_texts and review_ratings:
                for review, rating in zip(review_texts, review_ratings):
                    review_text = review.get_text(strip=True)
                    review_rating = int(rating.get_text(strip=True))
                    all_reviews.append((review_text, review_rating))
                page_number += 1
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f'Error al obtener la página de reviews {page_number} para la película con ID {movie_id}: {e}')
            break
    
    return all_reviews

def reviews_already_scraped(movie_id):
    if not os.path.isfile('reviews.csv'):
        return False
    
    with open('reviews.csv', mode='r', newline='', encoding='utf-8') as reviews_file:
        reviews_reader = csv.reader(reviews_file)
        for row in reviews_reader:
            if row and row[0] == movie_id:
                return True
    return False

def get_last_scraped_movie_id():
    if not os.path.isfile('reviews.csv'):
        return None
    
    with open('reviews.csv', mode='r', newline='', encoding='utf-8') as reviews_file:
        reviews_reader = csv.reader(reviews_file)
        last_row = None
        for row in reviews_reader:
            last_row = row
        if last_row:
            return last_row[0]  # Asumiendo que el ID de la película está en la primera columna
    return None

def obtener_portada_url(movie_id):
    movie_page_url = f'https://www.filmaffinity.com/es/film{movie_id}.html'
    try:
        response = requests.get(movie_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        portada_div = soup.find('a', class_='lightbox')
        if portada_div and 'href' in portada_div.attrs:
            return portada_div['href']
    except requests.exceptions.RequestException as e:
        print(f'Error al obtener la portada para la película con ID {movie_id}: {e}')
    return None

def limpiar_comentario(comentario):
    # Eliminar caracteres irrelevantes (puedes ajustar la expresión regular según sea necesario)
    comentario_limpio = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', comentario)
    comentario_limpio = comentario_limpio.strip()
    return comentario_limpio

# Verifica si el archivo CSV de películas ya existe
movies_file_exists = os.path.isfile('movies.csv')

# Abre el archivo CSV para escribir los datos de las películas
with open('movies.csv', mode='a' if movies_file_exists else 'w', newline='', encoding='utf-8') as movies_file:
    movies_writer = csv.writer(movies_file)
    if not movies_file_exists:
        movies_writer.writerow(['Título', 'Enlace', 'ID', 'Año', 'Enlace de la Portada'])
    
    # Verifica si el archivo CSV de reviews ya existe
    reviews_file_exists = os.path.isfile('reviews.csv')
    
    # Abre el archivo CSV para escribir los comentarios y sus puntuaciones
    with open('reviews.csv', mode='a' if reviews_file_exists else 'w', newline='', encoding='utf-8') as reviews_file:
        reviews_writer = csv.writer(reviews_file)
        if not reviews_file_exists:
            reviews_writer.writerow(['ID', 'Comentario', 'Puntuación'])
        
        last_scraped_movie_id = get_last_scraped_movie_id()
        start_scraping = False if last_scraped_movie_id else True
        
        for year in range(2021, 2025):
            url = f'https://www.filmaffinity.com/es/topgen.php?genres=&chv=0&orderby=rc&movietype=full%7C&country=&fromyear={year}&toyear={year}&ratingcount=2&runtimemin=0&runtimemax=7'
            
            try:
                response = requests.get(url)
                if response.status_code == 429:
                    print(f'Error 429: Too Many Requests for year {year}. Skipping to next year.')
                    continue
                response.raise_for_status()
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    movie_titles = soup.find_all('div', class_='mc-title')
                    
                    if movie_titles:
                        for movie in movie_titles:
                            link = movie.find('a')
                            if link and 'href' in link.attrs:
                                movie_url = link['href']
                                movie_title = link.get_text(strip=True)
                                movie_id_match = re.search(r'film(\d+)\.html', movie_url)
                                if movie_id_match:
                                    movie_id = movie_id_match.group(1)
                                    
                                    if not start_scraping:
                                        if movie_id == last_scraped_movie_id:
                                            start_scraping = True
                                        continue
                                    
                                    print(f'Título de la película: {movie_title}')
                                    print(f'ID de la película: {movie_id}')
                                    
                                    portada_url = obtener_portada_url(movie_id)
                                    movies_writer.writerow([movie_title, movie_url, movie_id, year, portada_url])
                                    
                                    if reviews_already_scraped(movie_id):
                                        print(f'Comentarios y puntuaciones ya listos para la película con ID {movie_id}.')
                                        continue
                                    
                                    all_reviews = get_all_reviews(movie_id)
                                    if all_reviews:
                                        print(f'Comentarios de la película con ID {movie_id}:')
                                        for review, rating in all_reviews:
                                            review_limpio = limpiar_comentario(review)
                                            puntuacion_ajustada = 1 if rating > 5 else 0
                                            reviews_writer.writerow([movie_id, review_limpio, puntuacion_ajustada])
                                        print(f'Total de comentarios mostrados: {len(all_reviews)}')
                                    else:
                                        print(f'No se encontraron comentarios para la película con ID {movie_id}.')
                                else:
                                    print('No se pudo extraer el ID de la película del enlace.')
                            else:
                                print('No se encontró un enlace en el título de película.')
                    else:
                        print(f'No se encontraron títulos de películas para el año {year}.')
                else:
                    print(f'La solicitud no fue exitosa para el año {year}.')
            except requests.exceptions.RequestException as e:
                print(f'Error al realizar la solicitud a la página principal para el año {year}: {e}')
