import pyodbc, os
from guide_creator.exceptions import DatabaseConnectionException, DatabaseOperationException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


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
                         {'sp': 'sp_get_winter_in_guide', 'name': 'Winter'},
                         {'sp': 'sp_get_breeding_in_guide', 'name': 'Breeding Season'},
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


class GoogleAPIUtilities(UtilitiesBase):
    def __init__(self, logger, scopes, cred_path, bird_root):
        self.scopes = scopes
        self.cred_path = cred_path
        self.bird_root = bird_root
        UtilitiesBase.__init__(self, logger=logger)

    def authenticate(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cred_path + 'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('drive', 'v3', credentials=creds)

    def list_folders_id_by_name(self, service):
        files = service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='" + self.bird_root + "'",
                                     spaces='drive', fields='nextPageToken, files(id, name)').execute()
        # there should only be one but if more this gets the first on
        return files['files'][0]['id']

    def list_all_folders_py_parent(self, service, file_id):
        folders = service.files().list(q="mimeType='application/vnd.google-apps.folder' and '" +
                                       file_id + "' in parents", spaces='drive',
                                       fields='nextPageToken, files(id, name)').execute()
        return folders

    def list_permissions_by_file_id(self, service, file_id):
        permissions = service.permissions().list(fileId=file_id, fields='*').execute()
        return permissions

    def delete_file_or_directory(self, service, file_id):
        service.files().delete(fileId=file_id).execute()

    def create_file_or_directory(self, service, item_name, parent_id):
        file_metadata = {
            'name': item_name,
            'parents': [parent_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file['id']

    def create_media_upload(self, service, media_name, media_path, parent_id):
        file_metadata = {
            'name': media_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(media_path + media_name,
                                mimetype='image/jpeg',
                                resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file['id']

    def create_permission(self, service, file_id, email):
        file_metadata = {
            'role': 'reader',
            'type': 'user',
            'emailAddress': email
        }
        permission = service.permissions().create(body=file_metadata, fileId=file_id).execute()
        return permission
