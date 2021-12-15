from guide_creater.utilites import SQLUtilities
from openpyxl import load_workbook


class GuideBase:
    def __init__(self, logger, sql_server_connection, guide_name):
        self.logger = logger
        self.sql_server_connection = sql_server_connection
        self.guide_name = guide_name
        self.clements = None
        self.guide_id = None

    def get_clements(self):
        return self.clements

    def set_clements(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_clements')
        self.clements = utilities.run_sql_return_no_params()

    def set_guide_id(self):
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_guide_id', params=' @GuideName=?', params_values=self.guide_name)
        a = utilities.run_sql_return_params()
        self.guide_id = utilities.run_sql_return_params()[0][0]

    def get_guide_id(self):
        return self.guide_id


class CreateGuide(GuideBase):
    def __init__(self, ebird_files, file_path, logger, sql_server_connection, guide_name, exotic_file=None,
                 targets_file=None):
        self.ebird_files = ebird_files
        self.file_path = file_path
        self.exotic_file = exotic_file
        self.targets_file = targets_file
        GuideBase.__init__(self, logger=logger, sql_server_connection=sql_server_connection, guide_name=guide_name)

    def _process_exotic_file(self, file_path, exotic_file, clements):
        return_list = []
        wb = load_workbook(file_path + exotic_file)
        sheetname = "Sheet1"
        ws = wb[sheetname]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1]:
                flag = False
                code = None
                english = None
                for taxon in clements:
                    if taxon[2] == row[2]:
                        flag = True
                        code = taxon[4]
                        english = taxon[1]
                if flag:
                    diction = {'name': english, 'code': code, 'scientific': row[2], 'target': ''}
                    return_list.append(diction)
                else:
                    self.logger.info('This exotic bird scientific name did not match Clements: '
                                     + row[2] + ', English: ' + row[1])
        return return_list

    def _process_ebird_file(self, path):
        my_wb = load_workbook(path)
        my_sheetname = "Sheet1"
        my_ws = my_wb[my_sheetname]
        raw_list = []
        for my_row in my_ws.iter_rows(min_row=2, values_only=True):
            raw_list.append(my_row[0])
        return_list = []
        for my_item in raw_list:
            if my_item:
                # todo add another line to ignore the new page line characters
                if 'sp.' not in my_item:
                    if '/' not in my_item:
                        if 'Domestic' not in my_item:
                            if 'undescribed' not in my_item:
                                if my_item != 'Jan':
                                    if ' x ' not in my_item:
                                        return_list.append(my_item.replace('\t', ''))
        return return_list

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
                self.logger.info('This ebird bird English name did not match Clements: ' + bird)
        return birds_clements

    def _combine_ebird_exotic(self, ebird_list, exotic_list):
        for exotic_bird in exotic_list:
            flag = False
            for ebird in ebird_list:
                if ebird['scientific'] == exotic_bird['scientific']:
                    flag = True
            if not flag:
                ebird_list.append(exotic_bird)
        return ebird_list

    def run_guide(self):
        self.logger.info('Start script execution.')
        self.set_clements()
        self.set_guide_id()
        clements = self.get_clements()
        utilities = SQLUtilities(logger=self.logger, sql_server_connection=self.sql_server_connection,
                                 sp='sp_get_all_birds')
        all_birds = utilities.run_sql_return_no_params()

        # collect all the ebird region files into one list then remove duplicates
        all_ebird_data = []
        for file in self.ebird_files:
            data = self._process_ebird_file(self.file_path + file)
            for item in data:
                all_ebird_data.append(item)
        distinct_ebird_list = self._remove_ebird_duplicates(all_ebird_data)

        # match ebird list to clements on english name and get scientific name and taxon code
        # if using the same clements version year there should be no logged mismatches
        distinct_ebird_list_clements = self._match_clements_ebird(self.get_clements(), distinct_ebird_list)

        # get exotic birds list and match to clements on scientific name, get clements english name and taxon code
        # log birds that don't match and fix these manually
        exotic_birds_clements = None
        if self.exotic_file:
            exotic_birds_clements = self._process_exotic_file(self.file_path, self.exotic_file, clements)

        # if there are any exotic birds then add the diff to the ebird list (no duplicates)
        all_birds_clements = []
        if exotic_birds_clements:
            all_birds_clements = self._combine_ebird_exotic(distinct_ebird_list_clements, exotic_birds_clements)
        else:
            all_birds_clements = distinct_ebird_list_clements

        # compare the ebird/exotic list to birds already in guides database
        # and create a final list for adding to the database
        add_list = []
        for final_bird in all_birds_clements:
            flag = False
            for master_bird in all_birds:
                if master_bird[1] == final_bird['name']:
                    flag = True
            if not flag:
                add = 'ADD'
            else:
                add = ''
            diction = {'name': final_bird['name'], 'code': final_bird['code'], 'scientific': final_bird['scientific'],
                       'add': add}
            add_list.append(diction)
        # todo add targets to list based on scientific name match


        # todo add only the new birds to Birds Table and all birds to the BirdsGuide table
        self.logger.info('End Script Execution.\n')
        pass

        # todo make an update guide method that looks for new birds for an existing guide from ebird regional lists

