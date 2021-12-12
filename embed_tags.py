import os, glob, pyodbc
from pyodbc import InterfaceError
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, USLT, TALB, TIT2, APIC, error, TPE1
from exceptions import DatabaseConnectionException, DatabaseOperationException


path_root = 'C:/temp/'
path_audio = path_root + 'Philippines Bird Guide/'
#path_audio = path_root + 'testing/'
path_audio_test = path_root + 'Audio Test/'
path_descriptions = path_root + 'Philippines Bird Descriptions/'
path_images = path_root + 'Philippines Bird Photos/'
path_mp3 = path_root + 'mp3/'


def connect_sqlserver():
    connection_string = "Driver={ODBC Driver 17 for SQL Server};"
    connection_string += "Server=localhost\\SQLEXPRESS;"
    connection_string += "Database=BirdGuide;"
    connection_string += "Trusted_Connection=yes;"
    try:
        conn = pyodbc.connect(connection_string)
    except (pyodbc.OperationalError, InterfaceError) as err:
        msg = 'Error connecting to database via odbc'
        raise DatabaseConnectionException(msg)
    return conn


def get_islands(name, code):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = sql = "EXEC sp_get_island_data @Bird_Name=?, @Taxanomic_Code=?"
    params = (name, code)
    try:
        cursor.execute(sql, params)
        data = cursor.fetchall()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


def get_brids(name, code):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = sql = "EXEC sp_get_birds @Bird_Name=?, @Taxanomic_Code=?"
    params = (name, code)
    try:
        cursor.execute(sql, params)
        data = cursor.fetchall()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


def get_all_birds():
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = sql = "select * from birds;"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get birds"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


def get_artist(name, code):
    conn = connect_sqlserver()
    cursor = conn.cursor()
    sql = sql = "EXEC sp_get_artist @Bird_Name=?, @Taxanomic_Code=?"
    params = (name, code)
    try:
        cursor.execute(sql, params)
        data = cursor.fetchone()
    except pyodbc.ProgrammingError as err:
        msg = "An error occurred executing a sql server command get artist"
        raise DatabaseOperationException(msg)
    conn.commit()
    return data


def parse_length(length_string):
    values = length_string.split('-')
    if values[0] == values[1]:
        return_value = values[0]
    else:
        return_value = length_string
    return return_value


def process_description(bird_data, island_data):
    return_data = ''
    for item in bird_data:
        return_data += item[0].strip() + ' (' + item[9] + ') ' + '\n'
        if len(item[1]) > 1:
            length = parse_length(item[1])
            return_data += length + ' in. '
        if len(item[2]) > 1:
            return_data += '; wingspan ' + item[2] + ' in. '
        if 'Least' not in item[3]:
            return_data += '; ' + item[3] + ' '
        if item[5]:
            return_data += '\nHABITAT: ' + item[5]
        if item[7]:
            return_data += '\nSONG: ' + item[7]
        return_data += '\n'
        for island in island_data:
            return_data += island[1] + '; ' + island[2] + '; ' + island[0]
            if island[3]:
                return_data += '; Target'
            # Endemic
            if island[5]:
                return_data += '; ' + island[5]
            return_data += '\n'
        return_data = return_data[:-1]
        if item[6]:
            return_data += '\nCONSERVATION: ' + item[6]
        if item[4]:
            return_data += '\nDESCRIPTION & MISC: ' + item[4]
        return_data += '\nRANGE: ' + item[10]
        return_data += '\n\nCREDITS:  '
        return_data += '\nData from "Birds of the World", Cornell University.'
        return_data += '\nAudio recordings from eBird, Cornell University.'
        return_data += '\nImages credits ("Artist"):\nA Guide to the Birds of the Philippines. Robert S. Kennedy, ' \
                       'Pedro C. Gonzales, Edward C. Dickinson, Hector C Miranda, Jr., and Timothy H. Fisher. Oxford ' \
                       'University Press. 2000'
        return_data += '\nBirds of the Greater Sundas, the Philippines, and Wallacea. Norman Arlott. ' \
                       'Princeton University Press. 2018.'
        return_data += '\nSibley Birds. David Allen Sibley. Second Edition. Alfred A. Knopf. 2014.'
        return_data += '\neBird, Cornell University.'
    return return_data


os.chdir(path_audio)
'''
data_birds = get_all_birds()
for bird in data_birds:
    flag = False
    for file in glob.glob('*'):
        fname = path_audio + file
        full_name = file.rsplit(".", 1)[0]
        prefix = full_name[:3].strip()
        name = full_name[3:].strip()
        test = bird[1].strip()
        if name.strip() == bird[1].strip():
            flag = True
    if not flag:
        print('Cant find this bird in files: ' + bird[1])

for file in glob.glob('*'):
    flag = False
    fname = path_audio + file
    full_name = file.rsplit(".", 1)[0]
    prefix = full_name[:3].strip()
    name = full_name[3:].strip()
    for bird in data_birds:
        test = bird[1]
        if bird[1] == name.strip():
            flag = True
    if not flag:
        print('Cant find this bird in database: ' + full_name)
'''

lst_images = []
for file in glob.glob('*'):
    fname = path_audio + file
    full_name = file.rsplit(".", 1)[0]
    prefix = full_name[:3].strip()
    name = full_name[3:].strip()
    data_birds = get_brids(name, prefix)
    data_islands = get_islands(name, prefix)
    lyrics = process_description(data_birds, data_islands)
    artist_data = get_artist(name, prefix)
    if artist_data:
        artist = artist_data[0]
    else:
        artist = ''
    try:
        tags = ID3(fname)
    except ID3NoHeaderError:
        tags = ID3()
    if len(tags.getall(u"USLT::'en'")) != 0:
        tags.delall(u"USLT::'en'")
        tags.save(fname)
    tags["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
    tags["USLT"] = (USLT(encoding=3, text=lyrics))
    tags["USLT::XXX"] = (USLT(encoding=3, text=lyrics))
    tags["TIT2"] = TIT2(encoding=3, text=full_name)
    tags["TPE1"] = TPE1(encoding=3, text=artist)
    tags["TALB"] = TALB(encoding=3, text=u'Philippines Bird Guide')
    tags.save(fname)
    audio = MP3(fname, ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass
    cover_file = path_images + full_name + '_' + artist + '.jpg'
    with open(cover_file, 'rb') as f:
        audio.tags.add(APIC(mime='image/jpeg', type=3, desc=u'Cover', data=open(cover_file, 'rb').read()))
    audio.save(fname)

