from guide_creator.utilites import SQLUtilities
import os, glob
from PIL import Image
from guide_creator.exceptions import VerifyFileException


class GuideBase:
    def __init__(self, logger, source_path):
        self.logger = logger
        self.source_path = source_path


class OptimizeImages(GuideBase):
    def __init__(self, optimize_path, source_path, logger):
        self.optimize_path = optimize_path
        GuideBase.__init__(self, logger=logger, source_path=source_path)

    def run_optimization(self):
        self.logger.info("Begin script execution to optimize images.")
        lst_images = []
        os.chdir(self.source_path)
        # todo add other image extensions
        files = glob.glob('*.gif')
        files.extend(glob.glob('*.png'))
        files.extend(glob.glob('*.jpg'))
        for file in files:
            lst_images.append(file.rsplit(".", 1)[0])
            image = Image.open(self.source_path + file)
            width, height = image.size
            if width > 800 or height > 800:
                ratio = width / height
                new_height = 800
                image = image.convert('RGB')
                new_width = int(ratio * new_height)
                image = image.resize((new_width, new_height))
                image.save(self.optimize_path + file.rsplit(".", 1)[0] + '.jpg', 'JPEG')
            else:
                image = image.convert('RGB')
                image.save(self.optimize_path + file.rsplit(".", 1)[0] + '.jpg', 'JPEG')
        self.logger.info("End script execution.")


class RenameAudioFiles(GuideBase):
    def __init__(self, source_path, destination_path, logger):
        self.destination_path = destination_path
        GuideBase.__init__(self, logger=logger, source_path=source_path)

    def run_rename(self):
        os.chdir(self.source_path)
        for file in glob.glob('*'):
            old_path = self.source_path + file
            if file[0] == 'z':
                new_path = self.source_path + file[1:].replace('_', "'")
            else:
                new_path = self.source_path + file.replace('_', "'")
            os.rename(old_path, new_path)

    def run_move(self):
        os.chdir(self.source_path)
        for file in glob.glob('*.mp3'):
            old_path = self.source_path + file
            new_path = self.destination_path + file
            os.rename(old_path, new_path)


class VerifyFileNames(GuideBase):
    def __init__(self, source_path, logger, sql_server_connection, is_image):
        self.sql_server_connection = sql_server_connection
        self.is_image = is_image
        GuideBase.__init__(self, logger=logger, source_path=source_path)

    def run_verification(self):
        self.logger.info("Begin script execution to verify image names.")
        if self.is_image:
            approved_ext = 'jpg'
        else:
            approved_ext = 'mp3'
        os.chdir(self.source_path)
        for file in glob.glob('*'):
            raw_name = file.rsplit(".", 1)[0]
            ext = file.rsplit(".", 1)[1]
            if ext != approved_ext:
                self.logger.error('Not an approved extension!!')
                self.logger.info("End script execution.\n")
                raise VerifyFileException
            # get artist for images only
            split_name = raw_name.split("_", 1)
            full_name = split_name[0]
            prefix = full_name[:4].strip()
            name = full_name[4:].strip()
            params = (name, prefix)
            utilities = SQLUtilities('sp_get_bird_id', self.logger, self.sql_server_connection,
                                     params='@BirdName=?,@TaxanomicCode=?', params_values=params)
            bird_id = utilities.run_sql_return_params()
            if not bird_id:
                self.logger.error('no match on bird name and code: ' + full_name)
                self.logger.info("End script execution.\n")
                raise VerifyFileException
            if self.is_image:
                try:
                    artist_name = split_name[1]
                except IndexError as err:
                    self.logger.error("Artist name not separated properly. " + full_name)
                    raise VerifyFileException
                utilities = SQLUtilities('sp_get_artist_id', self.logger, self.sql_server_connection,
                                         params='@ArtistName=?', params_values=artist_name)
                artist_id = utilities.run_sql_return_params()
                if not artist_id:
                    self.logger.error('no match or artist id: ' + full_name + ', artist name: ' + artist_name)
                    self.logger.info("End script execution.\n")
                    raise VerifyFileException
                params = (bird_id[0][0], artist_id[0][0])
                utilities = SQLUtilities('sp_update_bird_artist', self.logger, self.sql_server_connection,
                                         params='@BirdID=?, @ArtistID=?', params_values=params)
                utilities.run_sql_params()
        self.logger.info("End script execution.\n")
