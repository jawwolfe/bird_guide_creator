import pyodbc
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
