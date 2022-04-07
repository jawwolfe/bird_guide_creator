BEGIN HERE TO CERATE A BRAND NEW GUIDE
1) Add the ebird regions that your guide will contain. Manually or use run_get_eibrd_regions.py
2) Using Access Databse, add your guide to the guides table selecting the regions. If your guide has an Exotic Birding areas that matches your region add that name to the guides table.

BEGIN HERE TO ONLY REFRESH A GUIDE WITH NEW EBIRD DATA...
3) run_refresh_ebird_exotic_data.py  (pulls all the data from ebird website and the Exotic website if applicable.)
4) run_update_guides.py (adds the data from ebird and exotic raw data to the birds guides table)
5) run_update_todos.py (creates lists of the birds new to the database that will need images and audio files)

ONLY COMPLETE 6-9 IF YOUR REFRESH RESULTS IN NEW BIRDS W/O IMAGES OR AUDIO
6) Create all the images and put finished raw images into local Sources directory. Name them per the csv file using cut/paste.  Append the Artist after an underscore. 
7) Create all the audio files using the blank templates with the bird name. Put them into the Utilities directory.
8) run_process_audio_files.py (fixes apostrophes from drive download and checks names moves them to Audio Finished directory)
9) run_process_photo_files (optimized the images and moves them to Optimized directory)

SUPER GUIDE SETTINGS:  WHICH SUPERGUIES TO REFRESH TAGS AND UPLOAD
GUIDE REGIONS SETTINGS:  WHICH GUIDES WILL SHOW UP IN THE DESCRIPTION
10) run_embed_tags (add all the meta data to the audio file and uploads files to drive per the super guide settings.)
11) Run the DriveSync application on your phone to refresh you local directory. 
12) Download the appropriate playlists. If you added birds to the guide you will need to delete the old playlists and add the new ones.  
