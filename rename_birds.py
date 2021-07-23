import pyodbc, os, glob

path_root = 'C:/temp/'
path_photos = path_root + 'Philippines Bird Photos/'
#path_photos = path_root + 'test photo/'
path_audio = path_root + 'Philippines Bird Songs and Calls/'
#path_audio = path_root + 'test audio/'

connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)

sql = "exec sp_get_taxanomy;"
cursor = conn.cursor()
cursor.execute(sql)
data = cursor.fetchall()
conn.commit()
c = 0
os.chdir(path_audio)
for file in glob.glob('*'):
    full_name = file.rsplit(".", 1)[0].strip()
    prefix = full_name[:2].strip()
    name = full_name[2:].strip()
    for item in data:
        if item[1] == prefix and item[2] == name:
            old_path = path_audio + full_name + '.mp3'
            new_path = path_audio + item[0] + ' ' + name + '.mp3'
            print(old_path, new_path)
            os.rename(old_path, new_path)







