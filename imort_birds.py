import pyodbc, os, glob




path_root = 'C:/temp/'
path_audio = path_root + 'Philippines Bird Songs and Calls/'


#conn_str = "Server=localhost\SQLEXPRESS;Database=BirdGuide;Trusted_Connection=True;"
connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)



os.chdir(path_audio)
for file in glob.glob('*'):
    full_name = file.rsplit(".", 1)[0]
    prefix = full_name[:2].strip()
    name = full_name[2:].strip()
    sql = "Insert into Birds(BirdName, TaxanomicCode) values(?,?);"
    params = (name, prefix)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()








