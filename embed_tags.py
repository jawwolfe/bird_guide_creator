import os, glob
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, USLT, TALB, TIT2, APIC, error


path_root = 'C:/temp/'
path_audio = path_root + 'Philippines Bird Songs and Calls/'
path_audio_test = path_root + 'Audio Test/'
path_descriptions = path_root + 'Philippines Bird Descriptions/'
path_images = path_root + 'Philippines Bird Photos/'
path_mp3 = path_root + 'mp3/'

lst_images = []
os.chdir(path_mp3)
for file in glob.glob('*'):
    fname = path_root + 'mp3/' + file


    desc_file = path_descriptions + file.rsplit(".", 1)[0] + '.txt'
    with open(desc_file) as g:
        lyrics = g.read().strip()

    try:
        tags = ID3(fname)
    except ID3NoHeaderError:
        tags = ID3()

        # remove old unsychronized lyrics
    if len(tags.getall(u"USLT::'en'")) != 0:
        tags.delall(u"USLT::'en'")
        tags.save(fname)

        # tags.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
        # apparently the description is important when more than one
        # USLT frames are present
    tags["USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
    tags["USLT"] = (USLT(encoding=3, text=lyrics))
    tags["USLT::XXX"] = (USLT(encoding=3, text=lyrics))
    tags["TIT2"] = TIT2(encoding=3, text=file.rsplit( ".", 1 )[ 0 ])
    tags["TALB"] = TALB(encoding=3, text=u'Philippines Bird Songs and Calls')
    tags.save(fname)


    audio = MP3(fname, ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass

    cover_file = path_images + file.rsplit( ".", 1 )[ 0 ] + '.jpg'

    with open(cover_file, 'rb') as f:
        audio.tags.add(APIC(mime='image/jpeg', type=3, desc=u'Cover', data=open(cover_file,'rb').read()))
    audio.save(fname)
