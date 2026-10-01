import psycopg2
import psycopg2.extras

def connect():
  conn = psycopg2.connect(
    dbname = 'nom-votre-base',
    cursor_factory = psycopg2.extras.NamedTupleCursor
  )
  conn.autocommit = True
  return conn
