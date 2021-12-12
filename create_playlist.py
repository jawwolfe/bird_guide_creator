import pyodbc
from exceptions import DatabaseConnectionException, DatabaseOperationException
from pyodbc import InterfaceError

connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)


playlists_special = [{'sp': 'sp_get_in_guide', 'name': ''},
                     {'sp': 'sp_get_common_by_guide', 'name': 'Common Birds'},
                     {'sp': 'sp_get_common_uncommon_doves_by_guide', 'name': 'Common-Uncommon Doves and Cuckoos'},
                     {'sp': 'sp_get_common_passerines_by_guide','name': 'Common Passerines'},
                     {'sp': 'sp_get_common_scarce_passerines_by_guide', 'name': 'Common-Scarce Passerines'}]


path_create = "C:\\temp\\Playlists\\"
guide_id = 2
header = '#EXTM3U\n'
item_begin = '#EXTINF:'
extension = '.mp3\n'
folder = 'Birds/'


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


def get_phone_root(type):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    params = (type)
    sql = "Select Path from PhonePaths where Type = ?;"
    try:
        cursor.execute(sql, params)
        data = cursor.fetchone()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


def get_playlist_name(guide_id):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    params = (guide_id)
    sql = "Select GuideName from Guides where GuideID = ?;"
    try:
        cursor.execute(sql, params)
        data = cursor.fetchone()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


def get_birds(guide, sp):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = "EXEC " + sp + " @GuideID=?"
    params = (guide)
    try:
        cursor.execute(sql, params)
        data = cursor.fetchall()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


for item in playlists_special:
    guide = get_playlist_name(guide_id)
    sql_sp = item['sp']
    playlist_name = ''
    if item['name'] == '':
        playlist_name = guide[0] + ' Bird Guide'
    else:
        playlist_name = guide[0] + ' ' + item['name'] 
    root = get_phone_root('Android')[0]
    birds = get_birds(guide_id, sql_sp)
    str_file = header
    for item in birds:
        str_file += item_begin
        str_file += str(item[2]) + ',' + item[3] + " - "
        str_file += item[0] + ' ' + item[1] + '\n'
        str_file += root + folder + item[0] + ' ' + item[1] + extension

    f = open(path_create + playlist_name + '.m3u', "w")
    f.write(str_file)





