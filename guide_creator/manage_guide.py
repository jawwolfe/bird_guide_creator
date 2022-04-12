from guide_creator.utilites import SQLUtilities, ParseGuideAbundance
from guide_creator.exceptions import TaxonomyException
from collections import Counter
import shutil, datetime, os, sys
from bs4 import BeautifulSoup
import requests, json, datetime


class GuideBase:
    def __init__(self, logger, sql_server_connection):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.clements = None
        self.all_birds = None
        self.regions_birds = None
        self.exotic_guides_birds = None
        self.guides = None
        self.guides_birds = None

    def get_clements(self):
        return self.clements

    def set_clements(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_clements')
        self.clements = utilities.run_sql_return_no_params()

    def get_all_birds(self):
        return self.all_birds

    def set_all_birds(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_birds')
        self.all_birds = utilities.run_sql_return_no_params()

    def get_regions_birds(self):
        return self.regions_birds

    def set_regions_birds(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_regions_birds')
        self.regions_birds = utilities.run_sql_return_no_params()

    def get_exotic_guides_birds(self):
        return self.exotic_guides_birds

    def set_exotic_guides_birds(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                     sp='sp_get_exotic_guides_birds')
        self.exotic_guides_birds = utilities.run_sql_return_no_params()

    def get_guides(self):
        return self.guides

    def set_guides(self):
        utilities = SQLUtilities(sp='sp_get_guides', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        guides = utilities.run_sql_return_no_params()
        self.guides = guides


class CreateImageAudioTodoList(GuideBase):
    def __init__(self, logger, audio_guide_path, sql_server_connection, todo_path):
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection)
        self.audio_guide_path = audio_guide_path
        self.todo_path = todo_path

    def run(self):
        self.logger.info("Begin script execution.")
        self.set_guides()
        finished_birds = []
        for file in os.listdir(self.audio_guide_path):
            if file.endswith(".mp3"):
                prefix = file[0:4].strip()
                name = file[5:][:-4]
                diction = {'name': name, 'prefix': prefix}
                finished_birds.append(diction)
        utilities = SQLUtilities(sp='sp_get_all_birds', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        birds_database = utilities.run_sql_return_no_params()
        # delete all blank images before refreshing
        for audio in os.listdir(self.todo_path + 'Audio'):
            shutil.rmtree(self.todo_path + 'Audio\\' + audio)
        # delete all the list to dos.
        for todo_file in os.listdir(self.todo_path):
            if todo_file.endswith('csv'):
                os.remove(self.todo_path + todo_file)
        file = open(self.todo_path + 'Images_Needed' + '.csv', "w")
        for bird in birds_database:
            flag = False
            str_rg = ''
            for item in finished_birds:
                if bird[1] == item['name'] and bird[2] == item['prefix']:
                    flag = True
            if not flag:
                params = (bird[0])
                utilities = SQLUtilities(sp='sp_get_guides_regions_new', logger=self.logger,
                                         sql_server_connection=self.sql_server_connection,
                                         params_values=params, params=' @BirdID=?')
                regions_guides = utilities.run_sql_return_params()
                for rg in regions_guides:
                    str_rg += rg[0] + ', '
                file.write('"' + bird[2] + ' ' + bird[1] + '"' + ',"' + bird[3] + '"' + ',"' + str_rg + '"' + '\n')
        file.close()
        for guide in self.get_guides():
            utilities = SQLUtilities(sp='sp_get_birds_guide', logger=self.logger,
                                     sql_server_connection=self.sql_server_connection,
                                     params_values=guide[0], params=' @GuideID=?')
            birds_guide = utilities.run_sql_return_params()
            c = 0
            add_list = []
            for bird in birds_guide:
                flag = False
                for fin in finished_birds:
                    if bird[5] == fin['name']:
                        flag = True
                if not flag:
                    diction = {'code': bird[6], 'name': bird[5], 'scientific': bird[7]}
                    add_list.append(diction)
                    c += 1
            if c > 0:
                # create a directory for audio files
                os.mkdir(self.todo_path + 'Audio\\' + guide[1])
                f = open(self.todo_path + guide[1] + '.csv', "w")
                add_list = sorted(add_list, key=lambda d: d['code'])
                for item in add_list:
                    # move audio files into Audio guide dir
                    shutil.copy(self.todo_path + 'blank.mp3', self.todo_path + 'Audio\\' + guide[1] + '\\'
                                + item['code'] + ' ' + item['name'] + '.mp3')
                    f.write('"' + item['code'] + ' ' + item['name'] + '"' + ',"' + item['scientific'] + '"' + '\n')
                f.close()
        self.logger.info("End script execution.")


class ExoticParseUtility(GuideBase):
    def __init__(self, logger, exotic_base_url, sql_server_connection):
        self.exotic_base_url = exotic_base_url
        self.sql_server_connection = sql_server_connection
        self.targets = None
        self.specialities = None
        self.errors = None
        self.pages = ['/checklist.html', '/target-birds.html', '/special-birds.html']
        self.exclude = ['Streptopelia bitorquata', 'Aerodramus vanikorensis']
        self.char_map = {'/': 2, '\\': 3, '|': 8, '#': 7, '<': 6, '(': 4, '{': 5, '[': 9}
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection)

    def get_errors(self):
        return self.errors

    def set_errors(self):
        utilities = SQLUtilities(sp='sp_get_exotic_errors', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        errors = utilities.run_sql_return_no_params()
        self.errors = errors

    def get_targets(self, guide_id, scientific):
        return_data = []
        flag = False
        for item in self.targets:
            if item['scientific'] == scientific and item['guide'] == guide_id:
                flag = True
                return_data.append(item['likelihood'])
                return_data.append(1)
        if not flag:
            return_data.append('')
            return_data.append(0)
        return return_data

    def get_specialities(self, guide_id, scientific):
        return_data = []
        flag = False
        endemic_map = {'E': 1, 'NE': 2}
        conservation_map = {'NT': 2, 'V': 3, 'EN': 4, 'CR': 5}
        for item in self.specialities:
            if item['scientific'] == scientific and item['guide'] == guide_id:
                flag = True
                edem_val = ''
                cons_val = ''
                for key, val in endemic_map.items():
                    if key == item['endemic']:
                        edem_val = val
                for key, val in conservation_map.items():
                    if key == item['conservation']:
                        cons_val = val
                return_data.append(edem_val)
                return_data.append(cons_val)
        if not flag:
            return_data.append(5)
            return_data.append(1)
        return return_data

    def set_targets(self):
        all_data = []
        utilities = SQLUtilities(sp='sp_get_guides', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        guides = utilities.run_sql_return_no_params()
        for guide in guides:
            if guide[2]:
                guide_id = guide[0]
                # Get the checklist for this guide from exotic website
                url = self.exotic_base_url + guide[2] + self.pages[1]
                website = requests.get(url)
                soup = BeautifulSoup(website.content, 'html5lib')
                my_tables = soup.findAll("table")
                rows = my_tables[1].findChildren(['tr'])
                for row in rows:
                    tds = row.find_all('td')
                    diction = {'guide': guide_id, 'scientific': str(tds[2].find('i').contents[0].strip())}
                    all_data.append(diction)
        self.targets = all_data

    def set_specialities(self):
        all_data = []
        utilities = SQLUtilities(sp='sp_get_guides', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        guides = utilities.run_sql_return_no_params()
        for guide in guides:
            if guide[2]:
                guide_id = guide[0]
                # Get the checklist for this guide from exotic website
                url = self.exotic_base_url + guide[2] + self.pages[2]
                website = requests.get(url)
                soup = BeautifulSoup(website.content, 'html5lib')
                my_tables = soup.findAll("table")
                rows = my_tables[1].findChildren(['tr'])
                for row in rows:
                    tds = row.find_all('td')
                    diction = {'guide': guide_id, 'scientific': str(tds[2].find('i').contents[0].strip()),
                               'endemic': str(tds[3].contents[0].strip()), 'conservation': str(tds[4].contents[0].strip())}
                    all_data.append(diction)
        self.specialities = all_data

    def parse_chars(self, first_char):
        return_value = ''
        flag = False
        for key, val in self.char_map.items():
            if first_char == key:
                return_value = val
                flag = True
        if not flag:
            return_value = 1
        return return_value

    def parse_exotic_errors(self):
        self.set_errors()
        self.set_targets()
        self.set_specialities()
        self.set_exotic_guides_birds()
        for error in self.get_errors():
            # only process if this has not been entered before (entered = 0)
            if error[5] == 0:
                fl_exotic = False
                for item in self.exotic_guides_birds:
                    if item[0] == error[7] and item[1] == error[3]:
                        fl_exotic = True
                if not fl_exotic:
                    target_data = self.get_targets(error[3], error[1])
                    speciality_data = self.get_specialities(error[3], error[1])
                    params = (error[7], error[3], error[4], target_data[1],
                              speciality_data[0], speciality_data[1])
                    utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                             sp='sp_insert_exotic_checklist',
                                             params=' @BirdID=?, @GuideID=?, @ResidentStatusID=?, @Target=?, '
                                                    '@EndemicStatus=?, @ConservationStatus=?', params_values=params)
                    utilities.run_sql_params()
                    utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                             sp='sp_update_fix_exotic_error',
                                             params=' @ID=?', params_values=error[0])
                    utilities.run_sql_params()

    def parse_all_guides(self):
        self.logger.info('Start Execution.')
        self.set_clements()
        self.set_all_birds()
        self.set_exotic_guides_birds()
        self.set_targets()
        self.set_specialities()
        self.set_guides()
        guides = self.get_guides()
        c = 0
        for guide in guides:
            if guide[2]:
                guide_id = guide[0]
                self.set_errors()
                # Get the checklist for this guide from exotic website
                url = self.exotic_base_url + guide[2] + self.pages[0]
                website = requests.get(url)
                soup = BeautifulSoup(website.content, 'html5lib')
                my_tables = soup.findAll("table")
                rows = my_tables[1].findChildren(['tr'])
                row_ct = 0
                for row in rows:
                    if row_ct > 0:
                        bird_id = None
                        code = ''
                        bird_name_clements = ''
                        tds = row.find_all('td')
                        if len(tds) > 1:
                            flag_clement_match = False
                            flag_birds_match = False
                            scientific_name = tds[2].find('i').contents[0].strip()
                            c += 1
                            bird_name_exotic_raw = tds[1].contents[0].strip()
                            if bird_name_exotic_raw[0] in ['/', '\\', '|', '#', '(', '{', '[', '<'] and bird_name_exotic_raw[:-1][-2:] == '**':
                                bird_name_exotic = bird_name_exotic_raw[1:-1]
                                bird_name_exotic = bird_name_exotic[:-2]
                            elif bird_name_exotic_raw[0] in ['/', '\\', '|', '#', '(', '{', '[', '<']:
                                bird_name_exotic = bird_name_exotic_raw[1:-1]
                            elif bird_name_exotic_raw[-2:] == '**':
                                bird_name_exotic = bird_name_exotic_raw[:-2]
                            else:
                                bird_name_exotic = bird_name_exotic_raw
                            for taxon in self.get_clements():
                                # need to match on both Scientific and common name
                                if taxon[2] == scientific_name.strip() and taxon[1] == bird_name_exotic:
                                    if taxon[2] not in self.exclude:
                                        flag_clement_match = True
                                        code = taxon[4]
                                        bird_name_clements = taxon[1]
                            first_char = bird_name_exotic_raw[0]
                            res_status_id = self.parse_chars(first_char)
                            if not flag_clement_match:
                                self.logger.info('Exotic bird name not found in Clements: ' + bird_name_exotic +
                                                 ' checking for duplicate error.')
                                # add this bird to error table and break out of loop and go to next bird
                                # check for duplicates
                                fl_error = False
                                for error in self.get_errors():
                                    if error[1] == scientific_name and error[3] == guide_id:
                                        fl_error = True
                                if not fl_error:
                                    params = (bird_name_exotic, guide_id, res_status_id, scientific_name)
                                    utilities = SQLUtilities(logger=self.logger,
                                                             sql_server_connection=self.sql_server_connection,
                                                             sp='sp_insert_exotic_error',
                                                             params=' @BirdName=?,@GuideID=?,@ResidentStatusID=?, '
                                                                    '@ScientificName=?',
                                                             params_values=params)
                                    utilities.run_sql_params()
                                continue
                            # get the bird ID with scientific name
                            if 'arcuata' in scientific_name.strip():
                                pass
                            for bird in self.all_birds:
                                if bird[3] == scientific_name.strip():
                                    flag_birds_match = True
                                    bird_id = bird[0]
                            if not flag_birds_match:
                                # enter into birds table then exotic table
                                params = (bird_name_clements.strip(), code, scientific_name, 1006)
                                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                                         sp='sp_insert_bird',
                                                         params=' @BirdName=?,@TaxanomicCode=?,@ScientificName=?,@Artist=?',
                                                         params_values=params)
                                bird_id = utilities.run_sql_return_params()[0][0]
                                self.logger.info("Added a new bird to the Birds table: " + bird_name_clements.strip() +
                                                 ' ,id: ' + str(bird_id))
                                # refresh the all birds so this bird is not added again
                                self.set_all_birds()
                            fl_exotic = False
                            for item in self.exotic_guides_birds:
                                if item[0] == bird_id and item[1] == guide_id:
                                    fl_exotic = True
                            if not fl_exotic:
                                target_data = self.get_targets(guide_id, scientific_name)
                                speciality_data = self.get_specialities(guide_id, scientific_name)
                                params = (bird_id, guide_id, res_status_id, target_data[1],
                                          speciality_data[0], speciality_data[1])
                                utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                                         sp='sp_insert_exotic_checklist',
                                                         params=' @BirdID=?, @GuideID=?, @ResidentStatusID=?, @Target=?, '
                                                                '@EndemicStatus=?, @ConservationStatus=?',
                                                         params_values=params)
                                utilities.run_sql_params()
                    row_ct += 1
        self.logger.info('End script execution.')


class EbirdBarchartParseUtility(GuideBase):
    def __init__(self, logger, ebird_base_url, abundance_matrix, sql_server_connection):
        self.ebird_base_url = ebird_base_url
        self.abundance_matrix = abundance_matrix
        self.sql_server_connection = sql_server_connection
        self.barchart_suffix = '&yr=all&m='
        self.table_target = "table class=\"barChart\""
        self.bird_row_target = "rC_Row"
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection)

    def parse_all_regions(self):
        self.logger.info('Start Execution.')
        self.set_clements()
        self.set_all_birds()
        self.set_regions_birds()
        utilities = SQLUtilities(sp='sp_get_ebird_region_codes', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values='', params='')
        regions = utilities.run_sql_return_no_params()
        bird_ids_added = []
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
                                weeks = td.findAll("div")
                                for week in weeks:
                                    week_num += 1
                                    abundance = ''
                                    # get the 2 char class from the div tag (which has abundance number)
                                    raw_abun = str(week)[12:14]
                                    if raw_abun == 'sp':
                                        abundance = '0'
                                    if raw_abun[0] == 'b':
                                        # remove the leading b top get number 1-9
                                        abundance = raw_abun[1]
                                        if abundance == 'u':
                                            abundance = ''
                                    diction = {str(week_num): str(abundance)}
                                    scores.append(diction)
                if not skip_non_species and bird_name:
                    scores = json.dumps(scores)
                    bird_name = bird_name.strip()
                    # match this bird common name to Clements taxonomy
                    for taxon in self.get_clements():
                        if taxon[1] == bird_name.strip():
                            flag_clement_match = True
                            code = taxon[4]
                            scientific = taxon[2]
                    if not flag_clement_match:
                        # add this bird to error table and break out of loop and go to next bird
                        params = (bird_name, region_id, str(scores))
                        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                                 sp='sp_insert_region_abundance_err',
                                                 params=' @BirdName=?,@RegionID=?,@WeeksScores=?',
                                                 params_values=params)
                        utilities.run_sql_params()
                        continue
                    # get bird id with common name
                    # if not in birds table add it and return id
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
                        bird_ids_added.append(bird_id)
                        self.logger.info("Added a new bird to the Birds table: " + bird_name.strip() +
                                         ' ,id: ' + str(bird_id))
                        # refresh the all birds so this bird is not added again
                        self.set_all_birds()
                    # check to see if this combination of region and bird id is already in the database
                    # if already in update not not insert
                    fl_regions_birds = False
                    for item in self.regions_birds:
                        if item[0] == region_id and item[1] == bird_id:
                            fl_regions_birds = True
                    if not fl_regions_birds:
                        params = (bird_id, region_id, str(scores))
                        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                                 sp='sp_insert_region_abundance',
                                                 params=' @BirdID=?,@RegionID=?,@WeeksScores=?',
                                                 params_values=params)
                        utilities.run_sql_params()
                    else:
                        params = (bird_id, region_id, str(scores))
                        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                                 sp='sp_update_region_abundance',
                                                 params=' @BirdID=?,@RegionID=?,@WeeksScores=?',
                                                 params_values=params)
                        utilities.run_sql_params()
                row_ct += 1
        # add the new bird added to the file.
        self.logger.info("End script execution.")


class UpdateGuides(GuideBase):
    def __init__(self, logger, sql_server_connection, ebird_matrix):
        self.ebird_matrix = ebird_matrix
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection)

    def most_frequent(self, List):
        if len(List) > 0:
            occurence_count = Counter(List)
            return occurence_count.most_common(1)[0][0]
        else:
            return 0

    def get_birds_in_guide(self, guide_id):
        utilities = SQLUtilities(sp='sp_get_birds_guide', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values=(guide_id), params=' @GuideID=?')
        birds_guide = utilities.run_sql_return_params()
        return birds_guide

    def get_birds_ebird_guide(self, guide_id):
        utilities = SQLUtilities(sp='sp_get_ebird_birds_guide', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection,
                                 params_values=(guide_id), params=' @GuideID=?')
        birds_ebird = utilities.run_sql_return_params()
        return birds_ebird

    def process_abundance(self, abundance):
        c = 0
        summer = 0
        winter1 = 0
        winter2 = 0
        for char in abundance:
            if char == '':
                char = 0
            c += 1
            if c == 1:
                winter1 = char
            if c == 7:
                summer = char
            elif c == 12:
                winter2 = char
        total_winter = int(winter1) + int(winter2)
        average_winter = total_winter / 2
        if int(summer) == 0 and average_winter > 1:
            return 2
        else:
            return 1

    def run(self):
        self.logger.info("Start script execution.")
        self.set_guides()
        self.set_exotic_guides_birds()
        guides = self.get_guides()
        for guide in guides:
            utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                     params_values=guide[0], sp='sp_merge_birds_guides_raw_data',
                                     params=' @GuideID=?')
            utilities.run_sql_params()
            new_list = []
            birds_guides = self.get_birds_in_guide(guide[0])
            # get new birds just added in above merge query
            for bird in birds_guides:
                if bird[8] >= datetime.datetime.now() - datetime.timedelta(days=18):
                    new_list.append(bird[0])
            # see if these new entries were found in an exotic birds, if not then need to determine residency status
            for new_bird in new_list:
                flag = False
                for item in self.exotic_guides_birds:
                    if item[1] == guide[0] and new_bird == item[0]:
                        flag = True
                if not flag:
                    # get the residentStatus ID by passing in world region ID and bird ID
                    utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                             params_values=(new_bird, guide[3]), sp='sp_get_resident_by_world_region',
                                             params='@BirdID=?, @WorldRegionID=?')
                    resident_statuses = utilities.run_sql_return_params()
                    status_list = []
                    for status in resident_statuses:
                        status_list.append(status[0])
                    best_status = self.most_frequent(status_list)
                    if best_status == 0:
                        # can't find this bird's residency from other data so try to get it from ebird abundance data
                        parse_abundance = ParseGuideAbundance(self.logger, self.sql_server_connection,
                                                              self.ebird_matrix)
                        str_abundance = parse_abundance.calculate_region_abundance(new_bird, guide[0])
                        best_status = self.process_abundance(str_abundance[2])
                    params_values = (new_bird, guide[0], best_status)
                    utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                             params_values=params_values, sp='sp_update_bird_guide_residency',
                                             params='@BirdID=?,@GuideID=?,@ResidentID=?')
                    utilities.run_sql_params()
            self.logger.info("End script execution. ")
