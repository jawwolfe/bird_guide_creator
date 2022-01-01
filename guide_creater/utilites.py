import pyodbc, os
from guide_creater.exceptions import DatabaseConnectionException, DatabaseOperationException


class UtilitiesBase:
    def __init__(self, logger):
        self.logger = logger

    def connect_sqlserver(self, sqlserver_connection):
        connection_string = "Driver={ODBC Driver 17 for SQL Server};"
        connection_string += "Server=" + sqlserver_connection.name + ";"
        connection_string += "Database=" + sqlserver_connection.database + ";"
        connection_string += "Trusted_Connection=yes;"
        try:
            conn = pyodbc.connect(connection_string)
        except (pyodbc.OperationalError, pyodbc.InterfaceError) as err:
            msg = 'Error connecting to database via odbc: ' + str(err)
            self.logger.error(msg)
            raise DatabaseConnectionException(msg)
        return conn


class SQLUtilities(UtilitiesBase):
    def __init__(self, sp, logger, sql_server_connection, params=None, params_values=None):
        self.params = params
        self.params_values = params_values
        self.sql_server_connection = sql_server_connection
        self.sp = sp
        UtilitiesBase.__init__(self, logger=logger)

    def run_sql_return_no_params(self):
        conn = self.connect_sqlserver(self.sql_server_connection)
        cursor = conn.cursor()
        sql = "EXEC " + self.sp + ';'
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except pyodbc.ProgrammingError as err:
            msg = "An error occurred executing a sql server command"
            raise DatabaseOperationException(msg)
        conn.commit()
        cursor.close()
        conn.close()
        return data

    def run_sql_return_params(self):
        conn = self.connect_sqlserver(self.sql_server_connection)
        cursor = conn.cursor()
        sql = "EXEC " + self.sp + ' ' + self.params + ';'
        my_params = self.params_values
        try:
            cursor.execute(sql, my_params)
            data = cursor.fetchall()
        except pyodbc.ProgrammingError as err:
            msg = "An error occurred executing a sql server command"
            raise DatabaseOperationException(msg)
        conn.commit()
        cursor.close()
        conn.close()
        return data

    def run_sql_params(self):
        conn = self.connect_sqlserver(self.sql_server_connection)
        cursor = conn.cursor()
        sql = "EXEC " + self.sp + ' ' + self.params + ';'
        my_params = self.params_values
        try:
            cursor.execute(sql, my_params)
        except pyodbc.ProgrammingError as err:
            msg = "An error occurred executing a sql server command"
            raise DatabaseOperationException(msg)
        conn.commit()
        cursor.close()
        conn.close()


class BirdUtilities(UtilitiesBase):
    def __init__(self, logger, sql_server_connection, playlist_root, guide_id, guide_name):
        self.sql_server_connection = sql_server_connection
        self.playlist_root = playlist_root
        self.guide_id = guide_id
        self.guide_name = guide_name
        UtilitiesBase.__init__(self, logger=logger)

    def create_playlists(self):
        playlists_sps = [{'sp': 'sp_get_in_guide', 'name': ''},
                         {'sp': 'sp_get_common_by_guide', 'name': 'Common Birds'},
                         {'sp': 'sp_get_common_uncommon_doves_by_guide', 'name': 'Common-Uncommon Doves and Cuckoos'},
                         {'sp': 'sp_get_common_passerines_by_guide', 'name': 'Common Passerines'},
                         {'sp': 'sp_get_common_scarce_passerines_by_guide', 'name': 'Common-Scarce Passerines'}]
        header = '#EXTM3U\n'
        item_begin = '#EXTINF:'
        extension = '.mp3\n'
        folder_phone = 'Birds/'
        # todo get phone root from database
        root_phone = '/storage/emulated/0/'
        playlist_path = self.playlist_root + self.guide_name
        if not os.path.exists(playlist_path):
            os.mkdir(playlist_path)
        for item in playlists_sps:
            if item['name'] == '':
                playlist_name = self.guide_name + ' Bird Guide'
            else:
                playlist_name = self.guide_name + ' ' + item['name']
            utilities = SQLUtilities(item['sp'], self.logger, sql_server_connection=self.sql_server_connection,
                                     params_values=self.guide_id, params='@GuideID=?')
            birds = utilities.run_sql_return_params()
            str_file = header
            for bird in birds:
                str_file += item_begin
                str_file += str(bird[2]) + ',' + bird[3] + " - "
                str_file += bird[0] + ' ' + bird[1] + '\n'
                str_file += root_phone + folder_phone + bird[0] + ' ' + bird[1] + extension
            f = open(playlist_path + "\\" + playlist_name + '.m3u', "w")
            f.write(str_file)
