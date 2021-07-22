import os, glob, shutil

path_root = 'C:/temp/'
path_photos = path_root + 'Optimized/'

path_old = path_root + 'blank.mp3'
os.chdir(path_photos)
for file in glob.glob('*'):
    full_name = file.rsplit(".", 1)[0]
    path_new = path_root + 'Audio/' + full_name + '.mp3'
    shutil.copy(path_old, path_new)
