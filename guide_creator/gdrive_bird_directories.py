from guide_creator.utilites import SQLUtilities, GoogleAPIUtilities


class GDriveBirdDirectories:
    def __init__(self, logger, sql_server_connection, audio_path, google_api_scopes, google_cred_path,
                 root_guide_dir):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.audio_path = audio_path
        self.google_api_scopes = google_api_scopes
        self.google_cred_path = google_cred_path
        self.root_guide_dir = root_guide_dir

    def refresh(self):
        google_api = GoogleAPIUtilities(self.logger, self.google_api_scopes, self.google_cred_path,
                                        bird_root=self.root_guide_dir)
        service = google_api.authenticate()
        # get root directory id where all the bird directories will be found
        root_id = google_api.list_folders_id_by_name(service=service)

        folders_old = google_api.list_all_folders_py_parent(service=service, file_id=root_id)

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
            sg_name = super_guide[0]
            sg_id = super_guide[1]
            utilities = SQLUtilities('sp_get_birds_in_super_guide', self.logger,
                                     sql_server_connection=self.sql_server_connection,
                                     params_values=super_guide[1], params='@SuperGuideID=?')
            birds = utilities.run_sql_return_params()
            # create the directory
            new_folder_id = google_api.create_file_or_directory(service=service, item_name=sg_name, parent_id=root_id)
            # add the viewer permissions if matched to previous directory name
            for item in old_folders:
                if item['folder_name'] == sg_name:
                    for email in item['emails']:
                        new_perm_id = google_api.create_permission(service=service, file_id=new_folder_id, email=email)
            # upload audio files matching on Taxonomy and Name for that directory
            for bird in birds:
                google_api.create_media_upload(service=service, media_name=bird[0] + '.mp3', media_path=self.audio_path,
                                               parent_id=new_folder_id, mimetype='image/jpeg')
