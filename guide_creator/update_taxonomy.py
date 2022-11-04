import string, csv,os
from openpyxl import load_workbook
from guide_creator.utilites import SQLUtilities


class UpdateTaxonomy:
    def __init__(self, logger, sql_server_connection):
        self.logger = logger
        self.sql_server_connection = sql_server_connection

    def generate_code(self, species):
        add_list = []
        letters = []
        family_codes = []
        fpre = ''
        gpre = ''
        let = list(string.ascii_uppercase[0:26])
        let2 = list(string.ascii_uppercase[0:26])
        for l in let:
            for l2 in let2:
                letters.append(l + l2)
        for letter in let:
            for i in range(9):
                family_codes.append(letter + str(i+1))
        c = 0
        family = None
        genus = None
        g = 0
        for item in species:
            if family != item[1]:
                family = item[1]
                # create family prefix
                fpre = family_codes[c]
                c += 1
                g = 0
                # create genus prefix
                gpre = letters[g]
            else:
                if genus != item[2]:
                    genus = item[2]
                    # increment g prefix
                    g += 1
                    gpre = letters[g]
                else:
                    pass
            diction = {'order': item[0], 'group': family, 'code': fpre + gpre, 'english': item[3],
                       'scientific': item[4], 'range': '', 'changes': item[5]}
            add_list.append(diction)
        return add_list

    def search_list(self, mylist, needle):
        res = ''
        for item in mylist:
            if item['category'] == 'subspecies' or item['category'] == 'group (monotypic)':
                if needle in item['scientific']:
                    sub = item['scientific'][item['scientific'].rindex(' ')+1:]
                    res += (sub + ':  ' + item['range'] + '\n')
        return res

    def run_taxonomy_update(self):
        self.logger.info("Begin script execution to update taxonomy.")
        species_ranges = []
        raw_data = []
        utilities = SQLUtilities(sp='sp_get_clements_species', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        cl_species = utilities.run_sql_return_no_params()
        utilities = SQLUtilities(sp='sp_get_clements_species_subspecies', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        cl_species_subspecies = utilities.run_sql_return_no_params()
        # generates the unique sortable alpha numeric code list for all bird families in Clements taxonomy
        add_list = self.generate_code(cl_species)
        # get all the subspecies so collect the scientific name and range
        for item in cl_species_subspecies:
            diction = {'category': item[2], 'range': item[5], 'scientific': item[6]}
            raw_data.append(diction)
        # create range strings for each species from subspecies
        for item in raw_data:
            if item['category'] == 'species':
                if item['range'] == '':
                    if item['scientific'] == 'Crypturellus noctivagus':
                        pass
                    # this species has subspecies get all the ranges and ss name
                    species_range = self.search_list(raw_data, item['scientific'])
                else:
                    pass
                    # this species has no subspecies just get range
                    species_range = item['range']
                diction = {'scientific': item['scientific'], 'range': species_range}
                species_ranges.append(diction)
        # add ranges to list
        for add in add_list:
            for str_range in species_ranges:
                if add['scientific'] == str_range['scientific']:
                    add['range'] = str_range['range']
        # truncate the table "Clements"
        utilities = SQLUtilities(sp='sp_truncate_clements', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        utilities.run_sql()
        # insert finished taxonomy into database
        for i in add_list:
            params = (i['order'], i['code'], i['english'], i['scientific'], i['group'], i['range'], i['changes'])
            utilities = SQLUtilities(sp='sp_insert_clements', logger=self.logger, params_values=params,
                                     params='@order=?, @code=?, @english=?, @scientific=?, @ebirdgroup=?, @range=?, @changes=?',
                                     sql_server_connection=self.sql_server_connection)
            utilities.run_sql_params()
        self.logger.info("End script execution.")


class RepairUnmatchedFiles:
    def __init__(self, logger, image_path, guide_path, sql_server_connection):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.image_path = image_path
        self.guide_path = guide_path

    def compare(self, base_list, search_list):
        for base_item in base_list:
            flag = False
            for search_item in search_list:
                if base_item == search_item:
                    flag = True
            if not flag:
                print(base_item)

    def update_files_codes(self):
        pass


    def get_unmatched_files_by_name(self):
        # note all birds in guides should be equal to all those with completed audio
        utilities = SQLUtilities(sp='sp_get_all_audio_completed', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        db_birds = utilities.run_sql_return_no_params()
        birds = []
        for item in db_birds:
            birds.append(item[0][4:].strip())
        filenames_p = os.listdir(self.image_path)
        filenames_g = os.listdir(self.guide_path)
        guides = []
        photos = []
        for file in filenames_g:
            name_ext = file[4:].strip()
            name = name_ext[:-4]
            guides.append(name)
        for photo in filenames_p:
            split_name = photo.split("_", 1)
            name = split_name[0][4:].strip()
            photos.append(name)
        self.compare(birds, photos)
        self.compare(birds, guides)
        self.compare(photos, birds)
        self.compare(guides, birds)


class UpdateBLIConservation:
    def __init__(self, logger, sql_server_connection):
        self.logger = logger
        self.sql_server_connection = sql_server_connection

    def match_code(self, code):
        return_value = ''
        value_map = {'LC': 1, 'VU': 3, 'NT': 2, 'CR': 5, 'DD': 6, 'EN': 4, 'EW': 7, 'EX': 0, 'CR (PE)': 5}
        for k, v in value_map.items():
            if code == k:
                return_value = v
        return return_value

    def run(self):
        conservation_data = []
        with open('C:\\Users\\Andrew\\PycharmProjects\\bird_guide_creator\\data\\BLI_v6.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                line_count += 1
                if line_count > 0:
                    diction = {'english': row[2], 'scientific': row[3], 'code': row[4]}
                    conservation_data.append(diction)
        utilities = SQLUtilities(sp='sp_get_all_birds', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        all_birds = utilities.run_sql_return_no_params()
        for bird in all_birds:
            flag = False
            for taxon in conservation_data:
                if bird[3].strip() == taxon['scientific'].strip():
                    flag = True
                    my_code = self.match_code(taxon['code'])
                    utilities = SQLUtilities(sp='sp_update_conservation', logger=self.logger,
                                             sql_server_connection=self.sql_server_connection,
                                             params_values=(bird[0], my_code), params=' @BirdID=?, @ConservationID=?')
                    utilities.run_sql_params()
            if not flag:
                for item in conservation_data:
                    if item['english'] == bird[1]:
                        my_code = self.match_code(item['code'])
                        utilities = SQLUtilities(sp='sp_update_conservation', logger=self.logger,
                                                 sql_server_connection=self.sql_server_connection,
                                                 params_values=(bird[0], my_code),
                                                 params=' @BirdID=?, @ConservationID=?')
                        utilities.run_sql_params()
