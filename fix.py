from guide_creater.utilites import SQLUtilities
import datetime
from globals import initialize_sqlserver, initialize_logger


'''this was to recreate the csv file with the new birds for a guide to create images'''

utilities = SQLUtilities(sp='sp_get_new_birds_by_guide', sql_server_connection=initialize_sqlserver(),
                         params_values=12, params='@GuideID=?', logger=initialize_logger('bird_guide'))
new_image_list = utilities.run_sql_return_params()

guide_des = 'New_Guide ' + 'North Tunisia' + '_' + datetime.datetime.today().strftime('%Y-%m-%d')
image_path = 'C:\\temp\\Source\\'

f = open(image_path + guide_des + '.csv', "w")
for item in new_image_list:
    f.write('"' + item[0] + '"' + "\n")
f.close()
