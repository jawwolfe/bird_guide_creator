from guide_creator.utilites import SQLUtilities, GoogleAPIUtilities


class GDriveBirdDirectories:
    def __init__(self, logger, sql_server_connection, audio_path, google_api_scopes, google_cred_path):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.audio_path = audio_path
        self.google_api_scopes = google_api_scopes
        self.google_cred_path = google_cred_path

    def refresh(self):
        google_api = GoogleAPIUtilities(self.logger, self.google_api_scopes, self.google_cred_path,
                                        bird_root='Bird Guide Directories')
        service = google_api.authenticate()
        # get root directory id where all the bird directories will be found
        root_id = google_api.list_folders_id_by_name(service=service)
        print(root_id)

        folders_old = google_api.list_all_folders_py_parent(service=service, file_id=root_id)
        print(folders_old)

        # for each existing bird directory capture the directory name and viewer permission emails
        old_folders = []
        for folder in folders_old['files']:
            permissions = google_api.list_permissions_by_file_id(service=service, file_id=folder['id'])
            perms = []
            for perm in permissions['permissions']:
                if perm['role'] != 'owner':
                    perms.append(perm['emailAddress'])
            diction = {'folder_name': folder['name'], 'emails': perms}
            old_folders.append(diction)
            # then delete directory and all files
            google_api.delete_file_or_directory(service=service, file_id=folder['id'])

        # get the new bird directory names (called super guides in db) and their birds from the database
        utilities = SQLUtilities('sp_get_active_super_guides', self.logger,
                                 sql_server_connection=self.sql_server_connection)
        super_guides = utilities.run_sql_return_no_params()
        for super_guide in super_guides:
            utilities = SQLUtilities('sp_get_birds_in_super_guide', self.logger,
                                     sql_server_connection=self.sql_server_connection,
                                     params_values=super_guide[1], params='@SuperGuideID=?')
            birds = utilities.run_sql_return_params()
            # create the directory
    
            # add the viewer permissions if matched to previous directory name

            # upload audio files matching on Taxonomy and Name for that directory
