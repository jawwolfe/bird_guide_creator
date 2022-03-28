import datetime, json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, USLT, TALB, TIT2, APIC, error, TPE1
from guide_creator.utilites import SQLUtilities, GoogleDriveSuperGuide, PlaylistsSuperGuide


class EmbedTags:
    def __init__(self, logger, sql_server_connection, audio_path, image_path, playlist_root, google_api_scopes,
                 google_cred_path, super_guide_perm, ebird_matrix):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.audio_path = audio_path
        self.image_path = image_path
        self.playlist_root = playlist_root
        self.google_api_scopes = google_api_scopes
        self.google_cred_path = google_cred_path
        self.super_guide_perm = super_guide_perm
        self.ebird_matrix = ebird_matrix

    def parse_length(self, length_string):
        values = length_string.split('-')
        if values[0] == values[1]:
            return_value = values[0]
        else:
            return_value = length_string
        return return_value

    def translate_regions_abundance(self, raw_data):
        return_data = ''
        for myData in raw_data:
            for item in self.ebird_matrix:
                for key, val in item.items():
                    # insufficient data stored as empty string
                    if myData != '':
                        if val[0] < int(myData) <= val[1]:
                            return_data = return_data + key
            # has sufficient data but no observations stored as 0, show hyphen and space
            if myData == '0':
                return_data= return_data + '- '
            # insufficient data, stored as empty string, show asterisk
            if myData == '':
                return_data = return_data + '*'
        return return_data

    def calculate_region_abundance(self, bird_id, guide_id):
        # return series of 12 strings to represent the abundance of this bird in the guide for each month
        # for example:   -*-rsUCCs-- one for each month: JFMAMJJASOND, hpyhen + space = no observations,
        # * = insufficient data
        # max of each week in each month, max of each region
        str_regions_abundance = ''
        lst_regions_abundance = []
        params = (bird_id, guide_id)
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 params_values=params, sp='sp_get_abundance_data',
                                 params='@BirdID=?, @GuideID=?')
        regions_abundance = utilities.run_sql_return_params()
        abundance_raw = []
        for region in regions_abundance:
            c = 0
            abundance_raw_list = []
            # convert stored json string to json object
            big_list = json.loads(region[2])
            # split into 12 moth groups of 4 weeks each
            n = 4
            lists_of_lists = [big_list[i:i + n] for i in range(0, len(big_list), n)]
            for four_list in lists_of_lists:
                # create a list of the four values in each month and find the maximum value
                this_item = []
                for dict in four_list:
                    for key, value in dict.items():
                        this_item.append(value)
                my_result = max(this_item)
                abundance_raw_list.append(my_result)
            trans_data = self.translate_regions_abundance(abundance_raw_list)
            diction = {'region': region[1], 'country': region[0], 'data': trans_data}
            lst_regions_abundance.append(diction)
            for four_list in lists_of_lists:
                # create a list of the four values in each month and find the maximum value
                this_item = []
                for dict in four_list:
                    for key, value in dict.items():
                        this_item.append(value)
                my_result = max(this_item)
                # take the highest value from each set of 12
                if len(abundance_raw) >= 12:
                    if my_result > abundance_raw[c]:
                        abundance_raw[c] = my_result
                else:
                    abundance_raw.append(my_result)
                c += 1
        str_regions_abundance = self.translate_regions_abundance(abundance_raw)
        return [str_regions_abundance, lst_regions_abundance]

    def process_description(self, data_birds, data_islands, artist_data):
        return_data = ''
        for item in data_birds:
            t = datetime.datetime.now()
            updated = t.strftime('%m-%d-%Y')
            return_data += item[0].strip() + ' (' + item[9] + ') ' + '\n'
            if len(item[1]) > 1:
                length = self.parse_length(item[1])
                return_data += length + ' in. '
            if len(item[2]) > 1:
                return_data += '; wingspan ' + item[2] + ' in. '
            if 'Least' not in item[3]:
                return_data += '; ' + item[3] + ' '
            return_data += '\n'
            for island in data_islands:
                return_data += island[1] + '; ' + island[2]
                if island[3]:
                    return_data += '; Target'
                # Endemic
                if island[5].strip() != 'Not Endemic':
                    return_data += '; ' + island[5]
                str_abundance = self.calculate_region_abundance(item[11], island[6])
                return_data += '; ' + str_abundance[0] + '  ' + island[0]
                return_data += '\n'
            return_data = return_data[:-1]
            if item[5]:
                return_data += '\nHABITAT: ' + item[5]
            if item[7]:
                return_data += '\nSONG: ' + item[7]
            if item[6]:
                return_data += '\nCONSERVATION: ' + item[6]
            if item[4]:
                return_data += '\nDESCRIPTION & MISC: ' + item[4]
            return_data += '\n\nRANGE: ' + item[10]
            # put all the region abundance data here for all the guides label them with guide and region name
            return_data += '\n\nDETAIL ABUNDANCE REGIONS:'
            for guide in data_islands:
                return_data += '\n' + guide[1] + '\n'
                str_abundance = self.calculate_region_abundance(item[11], guide[6])
                for abun in str_abundance[1]:
                    return_data += abun['region'] + ', ' + abun['country'] + ': ' + abun['data'] + '\n'
            return_data += '\n\nCREDITS:  '
            # these credits are the same no matter which guide
            return_data += '\nData from "Birds of the World", Cornell University.'
            return_data += '\nAudio recordings from eBird, Cornell University.'
            return_data += '\nImages credits ("Artist"):  '
            # image credits by bird
            return_data += artist_data[0][3]
            return_data += ', authors: ' + artist_data[0][2]
            return_data += ', publisher: ' + artist_data[0][5]
            return_data += ', year: ' + str(artist_data[0][4])
            return_data += '\nLast Updated: ' + updated
        return return_data

    def run_embed(self):
        self.logger.info("Start script execution to embed tags.")
        # todo execute code to clean audio files (remove apostrophe) in the finished Directory
        utilities = SQLUtilities('sp_get_active_super_guides', self.logger,
                                 sql_server_connection=self.sql_server_connection)
        super_guides = utilities.run_sql_return_no_params()
        for super_guide in super_guides:
            sg_name = super_guide[0]
            sg_id = super_guide[1]
            utilities = SQLUtilities('sp_get_birds_in_super_guide', self.logger,
                                     sql_server_connection=self.sql_server_connection,
                                     params_values=sg_id, params='@SuperGuideID=?')
            birds = utilities.run_sql_return_params()
            for bird in birds:
                full_path_name = self.audio_path + bird[0] + '.mp3'
                prefix = bird[0][:4].strip()
                name = bird[0][4:].strip()
                full_name = bird[0]
                params_guides = (name, prefix, sg_name)
                params_birds = (name, prefix)
                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=params_guides, sp='sp_get_guide_data',
                                         params='@Bird_Name=?, @Taxanomic_Code=?, @SuperGuideName=?')
                data_guides = utilities.run_sql_return_params()
                utilities = SQLUtilities(sp='sp_get_bird_data', logger=self.logger, sql_server_connection=
                                         self.sql_server_connection, params='@Bird_Name=?, @Taxanomic_Code=?',
                                         params_values=params_birds)
                data_bird = utilities.run_sql_return_params()
                utilities = SQLUtilities(sp='sp_get_artist', logger=self.logger, sql_server_connection=
                                         self.sql_server_connection, params='@Bird_Name=?, @Taxanomic_Code=?',
                                         params_values=params_birds)
                artist_data = utilities.run_sql_return_params()
                lyrics = self.process_description(data_bird, data_guides, artist_data)
                if artist_data:
                    artist = artist_data[0][0]
                else:
                    artist = ''
                try:
                    tags = ID3(full_path_name)
                except ID3NoHeaderError:
                    tags = ID3()
                if len(tags.getall(u"USLT::'en'")) != 0:
                    tags.delall(u"USLT::'en'")
                    tags.save(full_path_name)
                tags["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
                tags["USLT"] = (USLT(encoding=3, text=lyrics))
                tags["USLT::XXX"] = (USLT(encoding=3, text=lyrics))
                tags["TIT2"] = TIT2(encoding=3, text=full_name)
                tags["TPE1"] = TPE1(encoding=3, text=artist)
                tags["TALB"] = TALB(encoding=3, text=sg_name)
                tags.save(full_path_name)
                audio = MP3(full_path_name, ID3=ID3)
                length = int(audio.info.length)
                params = (length, name, prefix)
                utilities = SQLUtilities(sp='sp_update_audio_length', logger=self.logger,
                                         sql_server_connection=self.sql_server_connection, params_values=params,
                                         params='@Length=?,@Bird_Name=?, @Taxanomic_Code=?')
                utilities.run_sql_params()
                try:
                    audio.add_tags()
                except error:
                    pass
                cover_file = self.image_path + full_name + '_' + artist + '.jpg'
                with open(cover_file, 'rb') as f:
                    audio.tags.add(APIC(mime='image/jpeg', type=3, desc=u'Cover', data=open(cover_file, 'rb').read()))
                audio.save(full_path_name)
            # refresh the google drive files for this super guide
            gdrive = GoogleDriveSuperGuide(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                           root_guide_dir='Bird Guide Directories',
                                           google_api_scopes=self.google_api_scopes,
                                           google_cred_path=self.google_cred_path, super_guide_id=sg_id,
                                           super_guide_name=sg_name, audio_path=self.audio_path,
                                           super_guide_perm=self.super_guide_perm)
            gdrive.refresh()
            # refresh the playlists for this super guide
            play = PlaylistsSuperGuide(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                       drive_root='Playlists Directories', playlist_root=self.playlist_root,
                                       google_api_scopes=self.google_api_scopes,
                                       google_cred_path=self.google_cred_path, super_guide_id=sg_id,
                                       super_guide_name=sg_name, super_guide_perm=self.super_guide_perm)
            play.refresh()
        self.logger.info("End script execution.")


class RefreshPlaylists:
    def __init__(self, logger, sql_server_connection, playlist_root, google_api_scopes,
                 google_cred_path, super_guide_perm):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.playlist_root = playlist_root
        self.google_api_scopes = google_api_scopes
        self.google_cred_path = google_cred_path
        self.super_guide_perm = super_guide_perm

    def run_refresh(self):
        self.logger.info("Start script execution to refresh playlists.")
        utilities = SQLUtilities('sp_get_active_super_guides', self.logger,
                                 sql_server_connection=self.sql_server_connection)
        super_guides = utilities.run_sql_return_no_params()
        for super_guide in super_guides:
            sg_name = super_guide[0]
            sg_id = super_guide[1]
            play = PlaylistsSuperGuide(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                       drive_root='Playlists Directories', playlist_root=self.playlist_root,
                                       google_api_scopes=self.google_api_scopes,
                                       google_cred_path=self.google_cred_path, super_guide_id=sg_id,
                                       super_guide_name=sg_name, super_guide_perm=self.super_guide_perm)
            play.refresh()
        self.logger.info("End script execution.")
