import pyodbc
from exceptions import DatabaseConnectionException, DatabaseOperationException
from pyodbc import InterfaceError

connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)


path_playlist = "C:\\Users\\awwolfe\\PycharmProjects\\audioembedder\\Cebu Common Passerines.m3u"
island_id = 2


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


def get_birds(island):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    #sql = "EXEC sp_get_in_island @islandid=?"
    #sql = "EXEC sp_get_common_by_island @IslandID=?"
    #sql = "EXEC sp_get_common_uncommon_doves_by_island @IslandID=?"
    sql = "EXEC sp_get_common_passarines_by_island @IslandID=?"
    params = (island)
    try:
        cursor.execute(sql, params)
        data = cursor.fetchall()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


birds = get_birds(island_id)

playlist = open(path_playlist, 'r')
c = 0
playlist_birds = []
for line in playlist:
    if '/storage/emulated/0/' in line:
        start = line.find("Guide/") + len("Guide/")
        end = line.find(".mp3")
        substring = line[start:end]
        prefix = substring[:3].strip()
        name = substring[3:].strip()
        #for bird in birds:
            #if bird[0] == prefix and bird[1] == name:
        myline = [prefix, name]
        playlist_birds.append(myline)

for item in playlist_birds:
    flag = False
    if item[1] == 'Eurasian Curlew':
        pass
    for bird in birds:
        if bird[0] == item[0] and bird[1] == item[1]:
            flag = True
    if not flag:
        print('Remove from playlist: ' + str(item))

for bird in birds:
    flag = False
    for line in playlist_birds:
        if bird[0] == line[0] and bird[1] == line[1]:
            flag = True
    if not flag:
        print('Add to playlist: ' + bird[0] + ' ' + bird[1])




