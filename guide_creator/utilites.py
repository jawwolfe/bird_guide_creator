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


class GoogleAPIUtilities(UtilitiesBase):
    def __init__(self, logger, scopes, cred_path, drive_root):
        self.scopes = scopes
        self.cred_path = cred_path
        self.drive_root = drive_root
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
        files = service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='" + self.drive_root + "'",
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

    def create_media_upload(self, service, media_name, media_path, parent_id, mimetype):
        file_metadata = {
            'name': media_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(media_path + media_name,
                                mimetype="'" + mimetype + "'",
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


class GoogleDriveSuperGuide:
    def __init__(self, logger, sql_server_connection, audio_path, google_api_scopes, google_cred_path,
                 root_guide_dir, super_guide_id, super_guide_name):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.audio_path = audio_path
        self.google_api_scopes = google_api_scopes
        self.google_cred_path = google_cred_path
        self.root_guide_dir = root_guide_dir
        self.super_guide_id = super_guide_id
        self.super_guide_name = super_guide_name

    def refresh(self):
        google_api = GoogleAPIUtilities(self.logger, self.google_api_scopes, self.google_cred_path,
                                        self.root_guide_dir)
        service = google_api.authenticate()
        # get root directory id where all the bird directories will be found
        root_id = google_api.list_folders_id_by_name(service=service)
        # find this superguide directory if it exists and get permissions then delete
        folders = google_api.list_all_folders_py_parent(service=service, file_id=root_id)
        permissions = None
        file_id = None
        for folder in folders['files']:
            if self.super_guide_name == folder['name']:
                file_id = folder['id']
                permissions = google_api.list_permissions_by_file_id(service=service, file_id=folder['id'])
        # then delete directory and all files
        if file_id:
            google_api.delete_file_or_directory(service=service, file_id=file_id)
        # create the directory
        new_folder_id = google_api.create_file_or_directory(service=service, item_name=self.super_guide_name,
                                                            parent_id=root_id)
        emails = []
        if permissions:
            for perm in permissions['permissions']:
                if perm['role'] != 'owner':
                    emails.append(perm['emailAddress'])
        if emails:
            for email in emails:
                new_perm_id = google_api.create_permission(service=service, file_id=new_folder_id, email=email)
        utilities = SQLUtilities('sp_get_birds_in_super_guide', self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values=self.super_guide_id, params='@SuperGuideID=?')
        birds = utilities.run_sql_return_params()
        # upload audio files
        for bird in birds:
            google_api.create_media_upload(service=service, media_name=bird[0] + '.mp3', media_path=self.audio_path,
                                           parent_id=new_folder_id, mimetype='image/jpeg')


class PlaylistsSuperGuide(GoogleAPIUtilities):
    def __init__(self, logger, sql_server_connection, playlist_root, drive_root, super_guide_id, super_guide_name,
                 google_api_scopes=None, google_cred_path=None):
        self.sql_server_connection = sql_server_connection
        self.playlist_root = playlist_root
        self.super_guide_id = super_guide_id
        self.super_guide_name = super_guide_name
        GoogleAPIUtilities.__init__(self, logger=logger, drive_root=drive_root, cred_path=google_cred_path,
                                    scopes=google_api_scopes)

    def refresh(self):
        google_api = GoogleAPIUtilities(self.logger, self.scopes, self.cred_path,
                                        drive_root=self.drive_root)
        service = google_api.authenticate()
        # get root directory id where all the bird directories will be found
        root_id = google_api.list_folders_id_by_name(service=service)
        # find this superguide directory if it exists and get permissions then delete
        folders = google_api.list_all_folders_py_parent(service=service, file_id=root_id)
        permissions = None
        file_id = None
        for folder in folders['files']:
            if self.super_guide_name == folder['name']:
                file_id = folder['id']
                permissions = google_api.list_permissions_by_file_id(service=service, file_id=folder['id'])
        # then delete directory and all files
        if file_id:
            google_api.delete_file_or_directory(service=service, file_id=file_id)
        # create the directory
        new_folder_id = google_api.create_file_or_directory(service=service, item_name=self.super_guide_name,
                                                            parent_id=root_id)
        emails = []
        if permissions:
            for perm in permissions['permissions']:
                if perm['role'] != 'owner':
                    emails.append(perm['emailAddress'])
        if emails:
            for email in emails:
                new_perm_id = google_api.create_permission(service=service, file_id=new_folder_id, email=email)
        # now get a list of active guides in this superguide and create director for each
        utilities = SQLUtilities('sp_get_active_guides_in_super_guide', self.logger,
                                 params_values=self.super_guide_id, params='@SuperGuideID=?',
                                 sql_server_connection=self.sql_server_connection)
        guides = utilities.run_sql_return_params()
        for guide in guides:
            new_guide_folder_id = google_api.create_file_or_directory(service=service, item_name=guide[0],
                                                                      parent_id=new_folder_id)
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
            playlist_path = self.playlist_root + guide[0]
            if not os.path.exists(playlist_path):
                os.mkdir(playlist_path)
            for item in playlists_sps:
                if item['name'] == '':
                    playlist_name = guide[0] + ' Bird Guide'
                else:
                    playlist_name = guide[0] + ' ' + item['name']
                utilities = SQLUtilities(item['sp'], self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=guide[1], params='@GuideID=?')
                birds = utilities.run_sql_return_params()
                str_file = header
                for bird in birds:
                    str_file += item_begin
                    str_file += str(bird[2]) + ',' + bird[3] + " - "
                    str_file += bird[0] + ' ' + bird[1] + '\n'
                    str_file += root_phone + folder_phone + bird[0] + ' ' + bird[1] + extension
                file_path = playlist_path + "\\" + playlist_name + '.m3u'
                f = open(file_path, "w")
                f.write(str_file)
                google_api.create_media_upload(service=service, media_name=playlist_name + '.m3u',
                                               media_path=playlist_path + '\\', parent_id=new_guide_folder_id,
                                               mimetype='audio/x-mpegurl')
