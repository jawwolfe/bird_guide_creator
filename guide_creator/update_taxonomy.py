import string
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
                       'scientific': item[4], 'range': ''}
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
        # generats the unique sortable alpha numeric code list for all bird families in Clements taxonomy
        add_list = self.generate_code(cl_species)
        # get all the subspecies so collect the scientific name and range
        for item in cl_species_subspecies:
            diction = {'category': item[2], 'range': item[5], 'scientific': item[6]}
            raw_data.append(diction)
        # create range strings for each species from subspecies
        for item in raw_data:
            if item['category'] == 'species':
                if item['range'] is None:
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
        # todo truncate the table "Clements"
        # insert finished taxonomy into database
        for i in add_list:
            params = (i['order'], i['code'], i['english'], i['scientific'], i['group'], i['range'])
            utilities = SQLUtilities(sp='sp_insert_clements_test', logger=self.logger, params_values=params,
                                     params='@order=?, @code=?, @english=?, @scientific=?, @ebirdgroup=?, @range=?',
                                     sql_server_connection=self.sql_server_connection)
            utilities.run_sql_params()
        self.logger.info("End script execution.")
