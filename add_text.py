import os,glob

path_root = 'C:/temp/'
path_descriptions = path_root + 'Philippines Bird Descriptions/'


os.chdir(path_descriptions)
for file in glob.glob('*'):
    file_edit = open(file, 'w')
    file_edit.write('Length  (Inches); Wingspan  (Inches); Resident; Least Concern; Endemic; Target Islands: ; Difficulty: \n\nHabitat\n\nConservation Status')


