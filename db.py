import psycopg2
from os import getenv

def insert_key(private_key):
    sql = """
        INSERT INTO keys (private)
        VALUES('{}')
        RETURNING id;
    """.format(
        private_key
    )
    conn = connection()
    cur = conn.cursor()
    cur.execute(sql)
    key_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return key_id

def get_key(key_id):
    sql = """
        SELECT private FROM keys
        WHERE id = {}
        LIMIT 1
    """.format(key_id)
    conn = connection()
    cur = conn.cursor()
    cur.execute(sql)
    private_key = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return private_key

def delete_key(key_id):
    sql = """
        DELETE FROM keys
        WHERE id = {}
    """.format(key_id)
    conn = connection()
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.close()
    return True

def connection():
    if (len(getenv('DATABASE_URL')) != 0):
        con_str = getenv('DATABASE_URL')
    else:
        con_str = 'postgres://{}:{}@{}:{}/{}'.format(
            getenv('DB_USER'),
            getenv('DB_PASS'),
            getenv('DB_SERVER'),
            getenv('DB_PORT'),
            getenv('DB_SCHEMA')
        )
    # print("Database connection string {}".format(con_str))
    return psycopg2.connect(con_str)

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        # print('Connecting to the PostgreSQL database...')
        conn = connection()

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        # print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        # print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            # print('Database connection closed.')
            return True
        return False

def migrate():
    """ Migrate database """
    commands = (
        """
        CREATE TABLE IF NOT EXISTS keys (
            id      SERIAL NOT NULL PRIMARY KEY,
            private TEXT   NOT NULL
        )
        """,
    )

    conn = None

    try:
        # connect to the PostgreSQL server
        conn = connection()
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            # print(command)
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
