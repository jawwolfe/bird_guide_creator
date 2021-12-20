import os, glob, datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, USLT, TALB, TIT2, APIC, error, TPE1
from guide_creater.utilites import SQLUtilities


class EmbedTags:
    def __init__(self, logger, sql_server_connection, audio_path, image_path):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.audio_path = audio_path
        self.image_path = image_path

    def parse_length(self, length_string):
        values = length_string.split('-')
        if values[0] == values[1]:
            return_value = values[0]
        else:
            return_value = length_string
        return return_value

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
            if item[5]:
                return_data += '\nHABITAT: ' + item[5]
            if item[7]:
                return_data += '\nSONG: ' + item[7]
            return_data += '\n'
            for island in data_islands:
                return_data += island[1] + '; ' + island[2] + '; ' + island[0]
                if island[3]:
                    return_data += '; Target'
                # Endemic
                if island[5].strip() != 'Not Endemic':
                    return_data += '; ' + island[5]
                return_data += '\n'
            return_data = return_data[:-1]
            if item[6]:
                return_data += '\nCONSERVATION: ' + item[6]
            if item[4]:
                return_data += '\nDESCRIPTION & MISC: ' + item[4]
            return_data += '\nRANGE: ' + item[10]
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
        os.chdir(self.audio_path)
        for file in glob.glob('*'):
            fname = self.audio_path + file
            full_name = file.rsplit(".", 1)[0]
            prefix = full_name[:4].strip()
            name = full_name[4:].strip()
            params = (name, prefix)
            utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                     params_values=params, sp='sp_get_guide_data',
                                     params='@Bird_Name=?, @Taxanomic_Code=?')
            data_guides = utilities.run_sql_return_params()
            utilities = SQLUtilities(sp='sp_get_bird_data', logger=self.logger, sql_server_connection=
                                     self.sql_server_connection, params='@Bird_Name=?, @Taxanomic_Code=?',
                                     params_values=params)
            data_bird = utilities.run_sql_return_params()
            utilities = SQLUtilities(sp='sp_get_artist', logger=self.logger, sql_server_connection=
                                     self.sql_server_connection, params='@Bird_Name=?, @Taxanomic_Code=?',
                                     params_values=params)
            artist_data = utilities.run_sql_return_params()
            lyrics = self.process_description(data_bird, data_guides, artist_data)
            if artist_data:
                artist = artist_data[0][0]
            else:
                artist = ''
            try:
                tags = ID3(fname)
            except ID3NoHeaderError:
                tags = ID3()
            if len(tags.getall(u"USLT::'en'")) != 0:
                tags.delall(u"USLT::'en'")
                tags.save(fname)
            tags["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
            tags["USLT"] = (USLT(encoding=3, text=lyrics))
            tags["USLT::XXX"] = (USLT(encoding=3, text=lyrics))
            tags["TIT2"] = TIT2(encoding=3, text=full_name)
            tags["TPE1"] = TPE1(encoding=3, text=artist)
            tags["TALB"] = TALB(encoding=3, text=u'Birds of the World')
            tags.save(fname)
            audio = MP3(fname, ID3=ID3)
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
            audio.save(fname)
            self.logger.info("End script execution.")
