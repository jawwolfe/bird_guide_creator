import string
from guide_creater.utilites import SQLUtilities


class UpdateTaxonomy:
    def __init__(self, logger, sql_server_connection):
        self.logger = logger
        self.sql_server_connection = sql_server_connection

    def run_taxonomy_update(self):
        utilities = SQLUtilities(sp='sp_get_clements_species', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        cl_species = utilities.run_sql_return_no_params()
        let = list(string.ascii_uppercase[0:26])
        let2 = list(string.ascii_uppercase[0:26])
        letters = []
        for l in let:
            for l2 in let2:
                letters.append(l + l2)
        family_codes = []
        for letter in let:
            for i in range(9):
                family_codes.append(letter + str(i+1))
        c = 0
        family = None
        genus = None
        g = 0
        add_list = []

        for item in cl_species:
            if family != item[1]:
                family = item[1]
                #print(family)
                # create family prefix
                fpre = family_codes[c]
                c += 1
                #print(fpre)
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
            # create new item
            dict = {'order': item[0], 'group': family, 'code': fpre + gpre, 'english': item[3], 'scientific': item[4], 'range': ''}
            add_list.append(dict)

        def search_list(list, needle):
            res = ''
            for item in list:
                if item['category'] == 'subspecies' or item['category'] == 'group (monotypic)':
                    if needle in item['scientific']:
                        sub = item['scientific'][item['scientific'].rindex(' ')+1:]
                        res += (sub + ':  ' + item['range'] + '\n')
            return res

        utilities = SQLUtilities(sp='sp_get_clements_species', logger=self.logger,
                                 sql_server_connection=self.sql_server_connection)
        cl_species_subspecies = utilities.run_sql_return_no_params()
        sql = "exec sp_get_clements_species_subspecies;"
        ranges = []
        range = None
        raw_data = []

        for item in cl_species_subspecies:
            dict = {'category': item[2], 'range': item[5], 'scientific': item[6]}
            raw_data.append(dict)

        for item in raw_data:
            if item['category'] == 'species':
                if item['range'] is None:
                    if item['scientific'] == 'Crypturellus noctivagus':
                        pass

                    # this species has subspecies get all the ranges and ss name
                    range = search_list(raw_data, item['scientific'])
                else:
                    pass
                    # this species has no subspecies just get range
                    range = item['range']
                dict = {'scientific': item['scientific'], 'range': range}
                ranges.append(dict)

        for add in add_list:
            for str_range in ranges:
                if add['scientific'] == str_range['scientific']:
                    add['range'] = str_range['range']

        for i in add_list:
            params = (i['order'], i['code'], i['english'], i['scientific'], i['group'], i['range'])
            utilities = SQLUtilities(sp='sp_update_clements', logger=self.logger, params_values=params,
                                     params='@order=?, @code=?, @english=?, @scientific=?, @ebirdgroup=?, @range=?',
                                     sql_server_connection=self.sql_server_connection)
            utilities.run_sql_params()
