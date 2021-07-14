import mutagen, os, glob
from PIL import Image

path_root = 'C:/temp/'
path_audio = path_root + 'Philippines Bird Songs and Calls/'
path_images = path_root + 'Philippines Bird Photos/'
#path_images = path_root + 'Photos/'
path_descriptions = path_root + 'Philippines Bird Descriptions/'
path_new_images = path_root + 'Photos New/'
test = path_root + 'Audio New/'

lst_images = []
os.chdir(test)
for file in glob.glob('*'):
    lst_images.append(file.rsplit( ".", 1 )[ 0 ] )
    image = Image.open(path_images + file)
    width, height = image.size
    if width > 800 or height > 800:
        ratio = width / height
        new_height = 800
        image = image.convert('RGB')
        new_width = int(ratio * new_height)
        image = image.resize((new_width, new_height))
        image.save(path_new_images + file.rsplit( ".", 1 )[ 0 ] + '.jpg', 'JPEG')
    else:
        image = image.convert('RGB')
        image.save(path_new_images + file.rsplit( ".", 1 )[ 0 ] + '.jpg','JPEG')
