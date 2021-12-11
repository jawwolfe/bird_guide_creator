import pyodbc, os, glob, sys

path_root = 'C:/temp/'
path_photos = path_root + 'Philippines Bird Photos/'
#path_photos = path_root + 'optimized/'
path_audio = path_root + 'Philippines Bird Guide/'
#path_audio = path_root + 'Audio/'

connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)

sql = "exec sp_get_names;"
cursor = conn.cursor()
cursor.execute(sql)
data = cursor.fetchall()
conn.commit()
c = 0
os.chdir(path_audio)

for file in glob.glob('*'):
    full_name = file.rsplit(".", 1)[0]
    prefix = full_name[:3].strip()
    name = full_name[3:].strip()

    for item in data:
        if name == item[0]:
            old_path = path_audio + full_name + '.mp3'
            new_path = path_audio + item[2] + ' ' + name + '.mp3'
            os.rename(old_path, new_path)

'''
for item in data:
    if item[0] != item[1]:
        old_path_image = path_photos + item[2] + ' ' + item[1] + '.jpg'
        new_path_image = path_photos + item[2] + ' ' + item[0] + '.jpg'
        os.rename(old_path_image, new_path_image)
        old_path_audio = path_audio + item[2] + ' ' + item[1] + '.mp3'
        new_path_audio = path_audio + item[2] + ' ' + item[0] + '.mp3'
        os.rename(old_path_audio, new_path_audio)

'''
