import os, glob, pyodbc
from pyodbc import InterfaceError
from exceptions import DatabaseConnectionException, DatabaseOperationException

path_root = 'C:/temp/'
path_new_images = path_root + 'Optimized/'

def connect_sqlserver():
    connection_string = "Driver={ODBC Driver 17 for SQL Server};"
    connection_string += "Server=localhost\\SQLEXPRESS;"
    connection_string += "Database=BirdGuide;"
    connection_string += "Trusted_Connection=yes;"
    try:
        conn = pyodbc.connect(connection_string)
    except (pyodbc.OperationalError, InterfaceError) as err:
        msg = 'Error connecting to database via odbc'
        raise DatabaseConnectionException(msg)
    return conn


def get_bird_id(name, code):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = sql = "Select BirdID from Birds where TaxanomicCode = ? and BirdName = ?"
    params = (code, name)
    try:
        cursor.execute(sql, params)
        myid = cursor.fetchone()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command to get bird"
        raise DatabaseOperationException(msg)
    conn.commit()
    return myid


def get_artist_id(name):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = sql = "Select ArtistID from Artists where ArtistName = ?"
    params = name
    try:
        cursor.execute(sql, params)
        myid = cursor.fetchone()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command to get artistid"
        raise DatabaseOperationException(msg)
    conn.commit()
    return myid


def update_bird_artist(birdid, artistid):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = "Update Birds set Artist = ? where BirdID = ?"
    params = (artistid, birdid)
    try:
        cursor.execute(sql, params)
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command to update bird with artist."
        raise DatabaseOperationException(msg)
    conn.commit()


os.chdir(path_new_images)
for file in glob.glob('*'):
    raw_name = file.rsplit(".", 1)[0]
    split_name = raw_name.split("_", 1)
    full_name = split_name[0]
    name = full_name[3:].strip()
    artist_name = split_name[1]
    prefix = full_name[:3].strip()
    artist_id = get_artist_id(artist_name)
    birdid = get_bird_id(name, prefix)
    update_bird_artist(birdid[0], artist_id[0])
