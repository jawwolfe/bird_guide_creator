import pyodbc, os, glob

path_root = 'C:/temp/'
path_audio = path_root + 'Optimized/'

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
    sql = "Insert into Birds(BirdName, TaxanomicCode) values(?,?); Select @@Identity as 'ID';"
    params = (name, prefix)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    sql = "Select @@Identity as 'ID';"
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    conn.commit()
    # default Cebu birds
    sql = 'Insert into BirdsIslands(BirdID, IslandID) values(?, 2);'
    params = (id)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()








