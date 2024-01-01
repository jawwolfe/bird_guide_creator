import datetime, json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, USLT, TALB, TIT2, APIC, error, TPE1
from guide_creator.utilites import SQLUtilities, GoogleDriveSuperGuide, PlaylistsSuperGuide, ParseGuideAbundance


class EmbedTags:
    def __init__(self, logger, sql_server_connection, audio_path, image_path, playlist_root, google_api_scopes,
                 google_cred_path, super_guide_perm, ebird_matrix, auto_drive):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.audio_path = audio_path
        self.image_path = image_path
        self.playlist_root = playlist_root
        self.google_api_scopes = google_api_scopes
        self.google_cred_path = google_cred_path
        self.super_guide_perm = super_guide_perm
        self.ebird_matrix = ebird_matrix
        self.auto_drive = auto_drive

    def parse_length(self, length_string):
        values = length_string.split('-')
        if values[0] == values[1]:
            return_value = values[0]
        else:
            return_value = length_string
        return return_value

    def get_region_count(self, guide_id):
        utilities = SQLUtilities(sp='sp_get_count_regions', logger=self.logger, params_values=guide_id,
                                 sql_server_connection=self.sql_server_connection, params=' @GuideID=?')
        region_count = utilities.run_sql_return_params()
        return region_count[0][0]

    def process_description(self, data_birds, data_islands, artist_data, alternatives_data, abundance_data_date):
        return_data = ''
        for item in data_birds:
            t = datetime.datetime.now()
            updated = t.strftime('%m-%d-%Y')
            return_data += item[0].strip() + ' (' + item[9] + ') ' + '\n'
            if alternatives_data:
                return_data += '('
                for name in alternatives_data:
                    return_data += name[0] + ', '
                return_data = return_data[:-2]
                return_data += ')\n'
            if len(item[1]) > 1:
                length = self.parse_length(item[1])
                return_data += length + ' in. '
            if len(item[2]) > 1:
                return_data += '; wingspan ' + item[2] + ' in. '
            if 'Least' not in item[3]:
                return_data += '; ' + item[3] + ' '
            return_data += '\n'
            for island in data_islands:
                return_data += island[7] + '; ' + island[2]
                if island[3]:
                    return_data += '; Target'
                # Endemic
                if island[5].strip() != 'Not Endemic':
                    return_data += '; ' + island[5]
                parse_abundance = ParseGuideAbundance(self.logger, self.sql_server_connection, self.ebird_matrix)
                str_abundance = parse_abundance.calculate_region_abundance(item[11], island[6])
                if str_abundance[0].strip():
                    return_data += '; ' + str_abundance[0]
                if island[4] in (6, 7):
                    return_data += '; ' + island[0]
                return_data += '\n'
            return_data = return_data[:-2]
            if item[15].strip():
                return_data += '\n' + item[15]
            if item[14]:
                return_data += '\nEBIRD OVERVIEW: ' + item[14]
            if item[13]:
                return_data += '\nIDENTIFICATION: ' + item[13]
            if item[5]:
                return_data += '\nHABITAT: ' + item[5]
            if item[12]:
                return_data += '\nMOVEMENT: ' + item[12]
            if item[7]:
                return_data += '\nSONG: ' + item[7]
            if item[4]:
                return_data += '\nBREEDING: ' + item[4]
            if item[6]:
                return_data += '\nCONSERVATION: ' + item[6]
            return_data += '\n\nRANGE (CLEMENTS): ' + item[10]
            # put all the region abundance data here for all the guides label them with guide and region name
            return_data += '\n\nDETAIL ABUNDANCE REGIONS:'
            guide_present = False
            for guide in data_islands:
                parse_abundance = ParseGuideAbundance(self.logger, self.sql_server_connection, self.ebird_matrix)
                str_abundance = parse_abundance.calculate_region_abundance(item[11], guide[6])
                num_regions = self.get_region_count(guide[6])
                # only show if more than one region
                # but if there is only one region but the guide has more than one region then show it anyhow
                # so user knows which region the data comes from
                if len(str_abundance[1]) > 1 or (len(str_abundance[1]) == 1 and num_regions > 1):
                    guide_present = True
                    return_data += '\n' + guide[1] + '\n'
                    for abun in str_abundance[1]:
                        return_data += abun['region'] + ', ' + abun['country'] + ': ' + abun['data'] + '\n'
            if not guide_present:
                # remove the heading for Detail Abundance because no guides has more than one region
                return_data = return_data[:-29]
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
            return_data += "\n(Abundance Refresh: " + str(abundance_data_date) + ")"
            return_data += '\nLast Guide Refresh: ' + updated
        return return_data

    def run_embed(self):
        self.logger.info("Start script execution to embed tags.")
        # todo execute code to clean audio files (remove apostrophe) in the finished Directory
        # is this in case I forget to run process audio before refreshing guides?
        utilities = SQLUtilities(sp='sp_get_active_super_guides', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        super_guides = utilities.run_sql_return_no_params()
        for super_guide in super_guides:
            sg_name = super_guide[0]
            sg_id = super_guide[1]
            utilities = SQLUtilities(sp='sp_get_birds_in_super_guide', logger=self.logger,
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
                utilities = SQLUtilities(sp='sp_get_bird_data', logger=self.logger,
                                         sql_server_connection=self.sql_server_connection,
                                         params='@Bird_Name=?, @Taxanomic_Code=?',
                                         params_values=params_birds)
                data_bird = utilities.run_sql_return_params()
                utilities = SQLUtilities(sp='sp_get_artist', logger=self.logger,
                                         sql_server_connection=self.sql_server_connection,
                                         params='@Bird_Name=?, @Taxanomic_Code=?',
                                         params_values=params_birds)
                artist_data = utilities.run_sql_return_params()
                utilities = SQLUtilities(sp='sp_get_alternatives_data', logger=self.logger,
                                         sql_server_connection=self.sql_server_connection,
                                         params='@Bird_Name=?, @Taxanomic_Code=?',
                                         params_values=params_birds)
                alternatives_data = utilities.run_sql_return_params()
                utilities = SQLUtilities(sp='sp_get_abundance_updated_date', logger=self.logger,
                                         sql_server_connection=self.sql_server_connection)
                abundance_date = utilities.run_sql_return_no_params()
                lyrics = self.process_description(data_bird, data_guides, artist_data, alternatives_data,
                                                  abundance_data_date=abundance_date[0][0])
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
                # Lyrics
                tags["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
                tags["USLT"] = (USLT(encoding=3, text=lyrics))
                tags["USLT::XXX"] = (USLT(encoding=3, text=lyrics))
                # Track name
                tags["TIT2"] = TIT2(encoding=3, text=full_name)
                # Artist
                tags["TPE1"] = TPE1(encoding=3, text=bird[1])
                # Album
                tags["TALB"] = TALB(encoding=3, text=sg_name + ' ' + artist)
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
            if self.auto_drive:
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
        utilities = SQLUtilities(sp='sp_get_active_super_guides', logger=self.logger,
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
