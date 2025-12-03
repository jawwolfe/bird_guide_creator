from guide_creator.update_taxonomy import UpdateTaxonomy, UpdateBLIConservation, RepairUnmatchedFiles
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
LOGGER = initialize_logger('bird_guide')
IMAGE_PATH = config.IMAGE_PATH_GUIDE
GUIDE_PATH = config.AUDIO_PATH_GUIDE

'''
STEP ONE:
Get the combined "eBird/Clements Checklist v202X" Excel version from
https://www.birds.cornell.edu/clementschecklist
Remove the First row of data which is not actually data
Remove all but 11 columns need to match dbo.Clements_202X table. Rename first column TAXON_ORDER. 
Make all other columns names with underscores to match DB fields. Save as CSV. 
DB, Tasks, Import from Flat File
All columns allow nulls, make 2 sort columns float, range and text for website nvarchar(max), all 
others nvarchar(255)

Backup the Clements table which will be truncated in the next step in case of errors. 
Backup Table:  Database, generate scripts, advanced, schema and data, then find replace name Clements 
to Clements_backup_year.  Change the two clements queries to use the appropriate new tables by incrementing the year 
sp_get_clements_species, sp_get_clements_species_subspecies

STEP TWO:
Run "UpdateTaxonomy", which will refresh the "Clements" table with the new taxonomy for Order, English, Scientific, 
and Range.  It also adds the custom sort code and the EbirdGroup. 

** NOTE: NEXT YEAR 2026 NEED TO ADD THE TEXT FOR THE CHANGES TO THE UPDATE TAXONOMY CODE.**
** OR can use the Update query after the fact to add text**

STEP THREE:
First manually go through the birds with both English and Scientific name changes and update English name in BirdName table
(use the Edit top X and add on order by)

using the saved queries:
Next joining on English Name Update the Scientific Name for all birds that had S.N. change
Then joining on Scientific Name Update the English Names for all birds that had E.N. change

Make query to get the different kinds of changes from the Clements table
Go through splits and lumps relevant to Birds table (link on SN or EN) and make spreadsheet per last year.

Splits: edit the scientific and/or English name as appropriate. New additions will happen during next refresh
Lumps: remove rows in Birds, BirdsGuides, and ExoticChecklists as appropriate (these will become orphans)
(***if remove a bird you must also remove the files in Photos and Mp3 directories***)
Remove all Splits from ExoticChecklist table (be careful because an Exotic refresh will readd these unless you change the code)

STEP FOUR
Once the Scientific names all fixed in Birds table do this:
TaxononmicSort code needs updated in Birds table from Clements table in case new generea were added or changed
Run the update query to update all Taxonomic Sort in Birds from Code in Clements join on Scientific name

STEP FIVE
The photos and mps files need to be changed to reflect changes in English names and Taxonomic Sort Codes
First find unmatched English Names using code. Fix manually in both Photos and Guides.  
Then run code to update all the Sort Code in photos and guides directories using English Name to match Birds table. 

STEP 6
Manually truncate the BirdsRegionsAbundance table so it is completely refreshed.

STEP 6.5  Edit the bird playlist queries that hard code the taxonomy codes and order ID which have probably changed

STEP 7
Run an entire refresh up until Embed Tags.  The new birds from the splits should be automatically added in the refresh. 

STEP 8 Add new photos and audio from the TODO.  Add/edit metadata where noted in my spreadsheet for splits and lumps
After finished run "Embed Tags" and "Refresh Playlists".  Note:  all playlists will need to up updated and reinstalled. 

'''

'''
update_cons = UpdateBLIConservation(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update_cons.run()


update = UpdateTaxonomy(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update.run_taxonomy_update()
'''

find = RepairUnmatchedFiles(logger=LOGGER, sql_server_connection=initialize_sqlserver(), image_path=IMAGE_PATH,
                            guide_path=GUIDE_PATH)
#find.get_unmatched_files_by_name()
find.update_files_codes()

