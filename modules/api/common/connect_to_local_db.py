import psycopg2

def connect_to_local_db():
    connection = psycopg2.connect(database="ecowater", user="ecowater", password="ecowater", host="pg", port="5432")
    return connection

