from guide_creator.utilites import SQLUtilities
from openpyxl import load_workbook
from guide_creator.exceptions import TaxonomyException
import shutil, datetime, csv, os
from bs4 import BeautifulSoup
import requests, json


class GuideBase:
    def __init__(self, logger, sql_server_connection, guide_name, file_path):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.clements = None
        self.guide_id = None
        self.all_birds = None
        self.guide_name = guide_name
        self.file_path = file_path

    def get_clements(self):
        return self.clements

    def set_clements(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_clements')
        self.clements = utilities.run_sql_return_no_params()

    def set_guide_id(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_guide_id', params=' @GuideName=?', params_values=self.guide_name)
        self.guide_id = utilities.run_sql_return_params()[0][0]

    def get_guide_id(self):
        return self.guide_id

    def set_all_birds(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_birds')
        self.all_birds = utilities.run_sql_return_no_params()

    def get_all_birds(self):
        return self.all_birds

    def _process_ebird_files(self):
        bird_list = []
        utilities = SQLUtilities('sp_get_regions_by_guide_name', self.logger, self.sql_server_connection,
                                 params=' @GuideName=?', params_values=self.guide_name)
        regions = utilities.run_sql_return_params()
        for region in regions:
            file = region[1].replace(' ', '_') + '_' + region[0].replace(' ', '_') + '_' + 'Ebird.xlsx'
            my_wb = load_workbook(self.file_path + file)
            my_sheetname = "Sheet1"
            my_ws = my_wb[my_sheetname]
            raw_list = []
            for my_row in my_ws.iter_rows(min_row=1, values_only=True):
                raw_list.append(my_row[0])
            file_list = []
            for my_item in raw_list:
                if my_item:
                    # todo add another line to ignore the new page line characters
                    if 'sp.' not in my_item:
                        if '/' not in my_item:
                            if 'Domestic' not in my_item:
                                if 'undescribed' not in my_item:
                                    if my_item != 'Jan':
                                        if my_item != 'bird sp':
                                            if ' x ' not in my_item:
                                                file_list.append(my_item.replace('\t', ''))
            for item in file_list:
                bird_list.append(item)
        distinct_ebird_list = self._remove_ebird_duplicates(bird_list)
        return distinct_ebird_list

    def _remove_ebird_duplicates(self, mylist):
        distinct_ebird_data = []
        for bird in mylist:
            if bird not in distinct_ebird_data:
                distinct_ebird_data.append(bird)
        return distinct_ebird_data

    def _match_clements_ebird(self, clements, myebirds):
        # match to clements add scientific and taxon log any mismatches
        birds_clements = []
        for bird in myebirds:
            flag = False
            for taxon in clements:
                if taxon[1] == bird:
                    flag = True
                    diction = {'name': bird, 'code': taxon[4], 'scientific': taxon[2], 'target': ''}
                    birds_clements.append(diction)
            if not flag:
                msg = "This ebird bird English name" + bird + " didn't match the Clements taxonomy." \
                      " Please fix before proceeding"
                self.logger.error(msg)
                raise TaxonomyException(msg)
        return birds_clements

    def _check_new_add(self, mylist):
        flag = False
        for item in mylist:
            if item['add'] == 'ADD':
                flag = True
        return flag

    def _check_new_update(self, ebird, database):
        master_flag = False
        for bird in ebird:
            flag = False
            for name in database:
                if bird['name'] == name[1]:
                    flag = True
            if not flag:
                master_flag = True
        return master_flag


class EbirdBarchartParseUtility(GuideBase):
    def __init__(self, logger, ebird_base_url, abundance_matrix, sql_server_connection, guide_name=None,
                 file_path=None):
        self.ebird_base_url = ebird_base_url
        self.abundance_matrix = abundance_matrix
        self.sql_server_connection = sql_server_connection
        self.barchart_suffix = '&yr=all&m='
        self.table_target = "table class=\"barChart\""
        self.bird_row_target = "rC_Row"
        self.guide_name = guide_name
        self.file_path = file_path
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection, guide_name=guide_name,
                           file_path=file_path)

    def parse_all_regions(self):
        self.logger.info('Start Execution.')
        self.set_clements()
        self.set_all_birds()
        utilities = SQLUtilities(sp='sp_get_ebird_region_codes', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        regions = utilities.run_sql_return_no_params()
        for region in regions:
            region_id = region[0]
            url = self.ebird_base_url + region[1] + self.barchart_suffix
            website = requests.get(url)
            soup = BeautifulSoup(website.content, 'html5lib')
            barchart_tables = soup.findAll("table", {"class": "barChart"})
            # Page has 2 tables with the class name skip first table
            my_table = barchart_tables[1]
            rows = my_table.findChildren(['tr'])
            row_ct = 0
            for row in rows:
                # skip first row of month labels
                td_ct = 0
                bird_name = ''
                flag_clement_match = False
                flag_all_birds_match = False
                code = None
                bird_id = None
                scientific = None
                skip_non_species = False
                scores = []
                if row_ct > 0:
                    week_num = 0
                    tds = row.find_all('td')
                    for td in tds:
                        td_ct += 1
                        # bird name is at first TD cell
                        if td_ct == 1:
                            # catch the non species birds as NoneType Attribute errors b/c there are no anchor tags
                            try:
                                bird_name = td.find('a').contents[0]
                            except AttributeError as err:
                                skip_non_species = True
                                continue
                        # 12 months are in rows 4-15
                        if td_ct >= 4 or td_ct <= 15:
                            if not skip_non_species and bird_name:
                                for taxon in self.get_clements():
                                    if taxon[1] == bird_name.strip():
                                        flag_clement_match = True
                                        code = taxon[4]
                                        scientific = taxon[2]
                                if not flag_clement_match:
                                    msg = 'This bird is not in the Clements Taxonomy by Common Name: ' + bird_name
                                    self.logger.error(msg)
                                    raise TaxonomyException(msg)
                                else:
                                    # get bird id, if not in Birds table add it
                                    pass
                                weeks = td.findAll("div")
                                for week in weeks:
                                    week_num += 1
                                    abundance = None
                                    # get the 2 char class from the div tag (which has abundance number)
                                    raw_abun = str(week)[12:14]
                                    if raw_abun == 'sp':
                                        abundance = 0
                                    if raw_abun[0] == 'b':
                                        # remove the leading b top get number 1-9
                                        abundance = raw_abun[1]
                                        if abundance == 'u':
                                            abundance = 0
                                    diction = {int(week_num): int(abundance)}
                                    scores.append(diction)
                if not skip_non_species and bird_name:
                    # print(code + '  ' + scientific)
                    for bird in self.all_birds:
                        if bird[1] == bird_name.strip():
                            flag_all_birds_match = True
                            bird_id = bird[0]
                    if not flag_all_birds_match:
                        params = (bird_name.strip(), code, scientific, 1006)
                        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                                 sp='sp_insert_bird',
                                                 params=' @BirdName=?,@TaxanomicCode=?,@ScientificName=?,@Artist=?',
                                                 params_values=params)
                        bird_id = utilities.run_sql_return_params()[0][0]
                        self.get_all_birds()
                    # get bird id with common name
                    # if not in birds table add it and return id
                    scores = json.dumps(scores)
                    # print(str(region_id) + ', ' + str(bird_id) + '  ' + str(scores))
                    params = (bird_id, region_id, str(scores))
                    utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                             sp='sp_insert_region_abundance',
                                             params=' @BirdID=?,@RegionID=?,@WeeksScores=?',
                                             params_values=params)
                    utilities.run_sql_params()
                    pass
                row_ct += 1


class CreateGuide(GuideBase):
    def __init__(self, file_path, logger, sql_server_connection, guide_name, audio_path, image_path,
                 playlist_root, test, root, targets_only, exotic_name=None):
        self.exotic_name = exotic_name
        self.targets_only = targets_only
        self.guide_name = guide_name
        self.file_path = file_path
        self.audio_path = audio_path
        self.image_path = image_path
        self.playlist_root = playlist_root
        self.test = test
        self.root = root
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection, guide_name=guide_name,
                           file_path=file_path)

    def _process_exotic_file(self):
        return_list = []
        file = 'Exotic_' + self.exotic_name.replace(' ', '_') + '.xlsx'
        wb = load_workbook(self.file_path + file)
        sheetname = "Sheet1"
        ws = wb[sheetname]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1]:
                flag = False
                code = None
                english = None
                for taxon in self.get_clements():
                    if taxon[2] == row[2]:
                        flag = True
                        code = taxon[4]
                        english = taxon[1]
                if flag:
                    diction = {'name': english, 'code': code, 'scientific': row[2], 'target': '', 'id': ''}
                    return_list.append(diction)
                else:
                    msg = "This exotic bird scientific name " + row[2] + " did not match Clements taxonomy, " \
                          "please fix before proceeding. English name: " + row[1]
                    self.logger.error(msg)
                    raise TaxonomyException(msg)
        return return_list

    def _get_targets(self):
        return_list = []
        file = 'Exotic_' + self.exotic_name.replace(' ', '_') + '_Targets.xlsx'
        wb = load_workbook(self.file_path + file)
        sheetname = "Sheet1"
        ws = wb[sheetname]
        for row in ws.iter_rows(min_row=1, values_only=True):
            if row[1]:
                diction = {'name': row[1], 'scientific': row[2]}
                return_list.append(diction)
        return return_list

    def _combine_ebird_exotic(self, ebird_list, exotic_list):
        for exotic_bird in exotic_list:
            flag = False
            for ebird in ebird_list:
                if ebird['scientific'] == exotic_bird['scientific']:
                    flag = True
            if not flag:
                ebird_list.append(exotic_bird)
        return ebird_list

    def run_create(self):
        self.logger.info('Start script execution to create Bird Guide.')
        self.set_clements()
        self.set_guide_id()
        clements = self.get_clements()
        guide_id = self.get_guide_id()
        targets = None
        if self.exotic_name:
            targets = self._get_targets()
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_birds')
        all_birds = utilities.run_sql_return_no_params()

        # collect all the ebird region files into one list then remove duplicates
        all_ebird_data = self._process_ebird_files()

        # match ebird list to clements on english name and get scientific name and taxon code
        # if using the same clements version year there should be no logged mismatches
        ebird_list_clements = self._match_clements_ebird(clements, all_ebird_data)

        # get exotic birds list and match to clements on scientific name, get clements english name and taxon code
        # log birds that don't match and fix these manually
        exotic_birds_clements = None
        all_birds_clements = None
        if self.exotic_name:
            exotic_birds_clements = self._process_exotic_file()

        # if there are any exotic birds then add the diff to the ebird list (no duplicates)
        # but only do this if we have the boolean to only update Targets to NO
        if not self.targets_only:
            if exotic_birds_clements:
                all_birds_clements = self._combine_ebird_exotic(ebird_list_clements, exotic_birds_clements)
            else:
                all_birds_clements = ebird_list_clements
        else:
            all_birds_clements = ebird_list_clements

        # add targets
        if self.exotic_name:
            for target in targets:
                for bird in all_birds_clements:
                    if target['scientific'] == bird['scientific']:
                        bird['target'] = 'TARGET'

        # compare the full list to birds already in guides database
        # and create a final list for adding to the database
        add_list = []
        for final_bird in all_birds_clements:
            flag = False
            id = None
            for master_bird in all_birds:
                if master_bird[1] == final_bird['name']:
                    flag = True
                    id = master_bird[0]
            if not flag:
                add = 'ADD'
            else:
                add = ''
            diction = {'name': final_bird['name'], 'code': final_bird['code'], 'scientific': final_bird['scientific'],
                       'add': add, 'target': final_bird['target'], 'id': id}
            add_list.append(diction)
        new_image_list = []
        # create paths for new images and audio files
        guide_des = 'New_Guide ' + self.guide_name + '_' + datetime.datetime.today().strftime('%Y-%m-%d')
        image_path = self.image_path
        audio_path = self.audio_path + guide_des + "\\"
        if self._check_new_add(add_list):
            try:
                os.mkdir(self.audio_path + guide_des)
            except FileExistsError as err:
                pass
        for add in add_list:
            target = 0
            if add['target'] == "TARGET":
                target = 1
            if add['add'] == "ADD":
                # add to birds database
                params_values = (add['name'], add['code'], add['scientific'], 1006)
                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=params_values, sp='sp_insert_bird',
                                         params='@BirdName=?,@TaxanomicCode=?,@ScientificName=?,@Artist=?')
                if self.test:
                    bird_id = 0
                else:
                    bird_id = utilities.run_sql_return_params()
                if self.test:
                    add['id'] = bird_id
                else:
                    add['id'] = bird_id[0][0]
                self.logger.info("Added new bird to database: " + add['name'])
                # todo calculate the Residency and Endemic status by looking at adjacent regions guides for this bird
                params_values = (add['id'], guide_id, 1, 2, target, 5)
                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=params_values, sp='sp_insert_bird_guide',
                                         params='@BirdID=?,@GuideID=?,@ResidentID=?,@Difficulty=?,@Target=?,@Endemic=?')
                if self.test:
                    pass
                else:
                    utilities.run_sql_params()
                self.logger.info("Added bird " + add['name'] + ' to the guide: ' + self.guide_name)
                diction = {'name': add['code'] + ' ' + add['name'], 'scientific': add['scientific']}
                new_image_list.append(diction)
                shutil.copy(self.audio_path + 'blank.mp3', audio_path + add['code'] + ' ' + add['name'] + '.mp3')

        # add the birds already in the database to the guide
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_in_guide', params='@GuideID=?', params_values=guide_id)
        guide_birds = utilities.run_sql_return_params()
        for add in add_list:
            flag = False
            target = 0
            if add['target'] == "TARGET":
                target = 1
            for name in guide_birds:
                if add['name'] == name[1]:
                    flag = True
            if not flag:
                params_values = (add['id'], guide_id, 1, 2, target, 5)
                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=params_values, sp='sp_insert_bird_guide',
                                         params='@BirdID=?,@GuideID=?,@ResidentID=?,@Difficulty=?,@Target=?,@Endemic=?')
                if self.test:
                    pass
                else:
                    utilities.run_sql_params()
                self.logger.info("Added bird " + add['name'] + ' to the guide: ' + self.guide_name)

        if self._check_new_add(add_list):
            f = open(self.root + guide_des + '.csv', "w")
            for item in new_image_list:
                f.write('"' + item['name'] + '"' + ',"' + item['scientific'] + '"' + '\n')
            f.close()
            self.logger.info("Playlist updated.")

        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 params_values=guide_id, params='@GuideID=?', sp='sp_update_guide_last_update')
        if self.test:
            pass
        else:
            utilities.run_sql_params()
        self.logger.info('End Script Execution.\n')


class UpdateGuide(GuideBase):
    def __init__(self, file_path, logger, sql_server_connection, guide_name, audio_path, image_path,
                 playlist_root, test, root):
        self.guide_name = guide_name
        self.file_path = file_path
        self.audio_path = audio_path
        self.image_path = image_path
        self.playlist_root = playlist_root
        self.test = test
        self.root = root
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection)

    def run_update(self):
        self.logger.info('Start script execution to update Bird Guide.')
        self.set_clements()
        self.set_guide_id()
        clements = self.get_clements()
        guide_id = self.get_guide_id()
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_birds')
        all_birds = utilities.run_sql_return_no_params()
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_in_guide', params='@GuideID=?', params_values=guide_id)
        guide_birds = utilities.run_sql_return_params()

        # collect all the ebird region files into one list then remove duplicates
        all_ebird_data = self._process_ebird_files()

        # get clements data
        ebird_list_clements = self._match_clements_ebird(clements, all_ebird_data)

        # create paths for new images and audio files
        guide_des = 'Updates_Guide ' + self.guide_name + '_' + datetime.datetime.today().strftime('%Y-%m-%d')
        image_path = self.image_path
        audio_path = self.audio_path + guide_des + "\\"

        new_image_list = []
        # check for birds new to the birds database
        if self._check_new_update(ebird_list_clements, all_birds):
            try:
                os.mkdir(self.audio_path + guide_des)
            except FileExistsError as err:
                pass
        for ebird in ebird_list_clements:
            flag = False
            for name in all_birds:
                if ebird['name'] == name[1]:
                    ebird['id'] = name[0]
                    flag = True
            if not flag:
                print('Not in Birds Database:' + ebird['name'])
                # add to birds database
                params_values = (ebird['name'], ebird['code'], ebird['scientific'], 1006)
                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=params_values, sp='sp_insert_bird',
                                         params='@BirdName=?,@TaxanomicCode=?,@ScientificName=?,@Artist=?')
                if self.test:
                    bird_id = 0
                else:
                    bird_id = utilities.run_sql_return_params()
                if self.test:
                    ebird['id'] = bird_id
                else:
                    ebird['id'] = bird_id[0][0]
                self.logger.info("Added new bird to database: " + ebird['name'])
                diction = {'name': ebird['code'] + ' ' + ebird['name'], 'scientific': ebird['scientific']}
                new_image_list.append(diction)
                shutil.copy(self.audio_path + 'blank.mp3', audio_path + ebird['code'] + ' ' + ebird['name'] + '.mp3')

        # check for birds new to the guide
        for ebird in ebird_list_clements:
            flag = False
            for name in guide_birds:
                if ebird['name'] == name[1]:
                    flag = True
            if not flag:
                print('Not in Birds Guide:' + ebird['name'])
                params_values = (ebird['id'], guide_id, 1, 2, 0, 5)
                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                         params_values=params_values, sp='sp_insert_bird_guide',
                                         params='@BirdID=?,@GuideID=?,@ResidentID=?,@Difficulty=?,@Target=?,@Endemic=?')
                if self.test:
                    pass
                else:
                    utilities.run_sql_params()
                self.logger.info("Added bird " + ebird['name'] + ' to the guide: ' + self.guide_name)

        if self._check_new_update(ebird_list_clements, all_birds):
            f = open(self.root + guide_des + '.csv', "w")
            for item in new_image_list:
                f.write('"' + item['name'] + '"' + ',"' + item['scientific'] + '"' + '\n')
            f.close()
            self.logger.info("Playlist updated.")

        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 params_values=guide_id, params='@GuideID=?', sp='sp_update_guide_last_update')
        if self.test:
            pass
        else:
            utilities.run_sql_params()
        self.logger.info("End script execution.")
