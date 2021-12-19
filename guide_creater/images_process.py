from guide_creater.utilites import SQLUtilities
import os, glob
from PIL import Image
from guide_creater.exceptions import VerifyImageException


class GuideBase:
    def __init__(self, logger, source_path, optimize_path):
        self.logger = logger
        self.source_path = source_path
        self.optimize_path = optimize_path


class Optimize(GuideBase):
    def __init__(self, optimize_path, source_path, logger):
        GuideBase.__init__(self, logger=logger, optimize_path=optimize_path,
                           source_path=source_path)

    def run_optimization(self):
        self.logger.info("Begin script execution to optimize images.")
        lst_images = []
        os.chdir(self.source_path)
        # todo add other image extensions
        for file in glob.glob('*.jpg'):
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


class Verify(GuideBase):
    def __init__(self, optimize_path, source_path, logger, sql_server_connection):
        self.sql_server_connection = sql_server_connection
        GuideBase.__init__(self, logger=logger, optimize_path=optimize_path, source_path=source_path)

    def run_verification(self):
        self.logger.info("Begin script execution to verify image names.")
        os.chdir(self.source_path)
        for file in glob.glob('*.jpg'):
            raw_name = file.rsplit(".", 1)[0]
            split_name = raw_name.split("_", 1)
            full_name = split_name[0]
            name = full_name[4:].strip()
            artist_name = split_name[1]
            prefix = full_name[:4].strip()
            utilities = SQLUtilities('sp_get_artist_id', self.logger, self.sql_server_connection,
                                     params='@ArtistName=?', params_values=artist_name)
            artist_id = utilities.run_sql_return_params()
            if artist_id:
                params = (name, prefix)
                utilities = SQLUtilities('sp_get_bird_id', self.logger, self.sql_server_connection,
                                         params='@BirdName=?,@TaxanomicCode=?', params_values=params)
                birdid = utilities.run_sql_return_params()
                if birdid:
                    params = (birdid[0][0], artist_id[0][0])
                    utilities = SQLUtilities('sp_update_bird_artist', self.logger, self.sql_server_connection,
                                             params='@BirdID=?, @ArtistID=?', params_values=params)
                    utilities.run_sql_params()
                else:
                    self.logger.error('no match on bird name and code: ' + full_name)
                    self.logger.info("End script execution.\n")
                    raise VerifyImageException
            else:
                self.logger.error('no match or artist id: ' + full_name + ', artist name: ' + artist_name)
                self.logger.info("End script execution.\n")
                raise VerifyImageException
        self.logger.info("End script execution.\n")
