import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from sqlalchemy import create_engine, text

# Ініціалізація Faker (українська локаль)
fake = Faker('uk_UA')
Faker.seed(42)
random.seed(42)

# Створення папки Data Lake, якщо її немає
os.makedirs('data_lake', exist_ok=True)
print("Починаємо генерацію даних для онлайн-кінотеатру...")

# 1. ТАБЛИЦІ ВИМІРІВ (DIMENSIONS)

def generate_directors():
    print("Генерація режисерів...")
    directors_list = ['Крістофер Нолан', 'Квентін Тарантіно', 'Джеймс Кемерон', 'Стівен Спілберг', 'Дені Вільньов', 'Мартін Скорсезе']
    data = []
    for i, dir_name in enumerate(directors_list):
        data.append({
            'director_id': i + 1,
            'director_name': dir_name,
            'country': fake.country()
        })
    return pd.DataFrame(data)

def generate_movies(n, director_ids):
    print(f"Генерація {n} фільмів...")
    genres = ['Фантастика', 'Драматичний', 'Комедія', 'Бойовик', 'Трилєр']
    data = []
    for i in range(1, n + 1):
        data.append({
            'movie_id': i,
            'director_id': random.choice(director_ids),
            'title': fake.catch_phrase(),
            'genre': random.choice(genres),
            'release_year': random.randint(2005, 2026),
            'price_per_view': round(random.uniform(50.0, 300.0), 2)
        })
    return pd.DataFrame(data)

def generate_subscribers(n):
    print(f"Генерація {n} підписників (з імітацією 'брудних даних')...")
    data = []
    for i in range(1, n + 1):
        email = fake.email() if random.random() > 0.1 else None
        data.append({
            'subscriber_id': i,
            'full_name': fake.name(),
            'email': email,
            'city': fake.city(),
            'subscription_tier': random.choice(['Basic', 'Standard', 'Premium']),
            'registration_date': fake.date_between(start_date='-2y', end_date='today')
        })
    
    df = pd.DataFrame(data)
    duplicates = df.sample(frac=0.05)
    df = pd.concat([df, duplicates], ignore_index=True)
    return df

# 2. ТАБЛИЦІ ФАКТІВ (FACTS)

def generate_views(n, subscriber_ids, movie_ids):
    print(f"Генерація {n} переглядів...")
    data = []
    for i in range(1, n + 1):
        data.append({
            'view_id': fake.uuid4(),
            'subscriber_id': random.choice(subscriber_ids),
            'movie_id': random.choice(movie_ids),
            'view_date': fake.date_time_between(start_date='-1y', end_date='now'),
            'watch_duration_minutes': random.randint(20, 180)
        })
    return pd.DataFrame(data)

# Таблиця reviews
def generate_reviews(n, subscriber_ids, movie_ids):
    print(f"Генерація {n} відгуків (reviews)...")
    data = []
    for i in range(1, n + 1):
        # Для 20% записів залишаємо comment порожнім (NULL), як вимагає методичка
        comment = fake.sentence(nb_words=8) if random.random() > 0.2 else None
        data.append({
            'review_id': fake.uuid4(),
            'product_id': random.choice(movie_ids),      # product_id
            'user_id': random.choice(subscriber_ids),     # user_id
            'rating': random.randint(1, 5),               # rating від 1 до 5
            'comment': comment                            # 20% NULL
        })
    return pd.DataFrame(data)

# 3. ОРКЕСТРАЦІЯ ТА ЗБЕРЕЖЕННЯ У DWH

df_directors = generate_directors()
df_movies = generate_movies(50, df_directors['director_id'].tolist())
df_subscribers = generate_subscribers(300)

unique_subscriber_ids = df_subscribers['subscriber_id'].dropna().unique().tolist()
movie_ids = df_movies['movie_id'].tolist()

df_views = generate_views(2000, unique_subscriber_ids, movie_ids)
df_reviews = generate_reviews(800, unique_subscriber_ids, movie_ids)

# Збереження у форматі Parquet
print("Збереження файлів у форматі Parquet...")
df_directors.to_parquet('data_lake/raw_directors.parquet', index=False)
df_movies.to_parquet('data_lake/raw_movies.parquet', index=False)
df_subscribers.to_parquet('data_lake/raw_subscribers.parquet', index=False)
df_views.to_parquet('data_lake/raw_views.parquet', index=False)
df_reviews.to_parquet('data_lake/raw_reviews.parquet', index=False)
print("Файли успішно збережено у папці /data_lake")

# Підключення та завантаження у PostgreSQL
DB_URL = "postgresql+psycopg2://admin:adminpassword@localhost:5432/cinema_dwh"
engine = create_engine(DB_URL)

def load_data_to_dwh():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()

    print("Завантаження directors...")
    df_directors.to_sql('directors', engine, schema='raw', if_exists='replace', index=False)
    
    print("Завантаження movies...")
    df_movies.to_sql('movies', engine, schema='raw', if_exists='replace', index=False)
    
    print("Завантаження subscribers...")
    df_subscribers.to_sql('subscribers', engine, schema='raw', if_exists='replace', index=False)
    
    print("Завантаження views...")
    df_views.to_sql('views', engine, schema='raw', if_exists='replace', index=False)
    
    print("Завантаження reviews...")
    df_reviews.to_sql('reviews', engine, schema='raw', if_exists='replace', index=False)
    
    print("Успіх! Усі дані успішно завантажені у схему 'raw' бази даних!")

if __name__ == "__main__":
    load_data_to_dwh()