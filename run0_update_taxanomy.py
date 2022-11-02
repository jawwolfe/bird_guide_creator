from guide_creator.update_taxonomy import UpdateTaxonomy, UpdateBLIConservation
from guide_creator.configs import config
from globals import initialize_logger, initialize_sqlserver

SQLSERVER_NAME = config.SQLSERVER_NAME
SQLSERVER_DATABASE = config.SQLSERVER_DATABASE
LOGGER = initialize_logger('bird_guide')


'''
STEP ONE:
Get the combined "eBird/Clements Checklist v202X" Excel version from
https://www.birds.cornell.edu/clementschecklist
Remove the First row of data which is not actually data
Use SSMS DB tasks, Import Data, Excel Source, Destination: "Microsoft OLE DB Provider for SQLServer"
Rename new table to "Clements_202X".  You may need to drop a number of "Phantom field" with no data

Add underscores to all field names and change the first column sort to "TAXON_ORDER"

STEP TWO:
Run "UpdateTaxonomy", which will refresh the "Clements" table with the new taxonomy for Order, English, Scientific, 
and Range.  It also adds the custom sort code and the EbirdGroup. 

Manually truncate the BirdsRegionsAbundance table.
Run the 

Scientific Name Change only: Script
English Name Change only: Script
Splits: add new rows in Birds and BirdGuides
Lumps: inactivate or remove rows in Birds and BirdsGuides

Once the Scieneific names all fixed in Birds table do this:
TaxononmicSrot code needs updated in Birds table from Clements table in case new generea were added
'''



'''
update_cons = UpdateBLIConservation(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update_cons.run()
'''


update = UpdateTaxonomy(logger=LOGGER, sql_server_connection=initialize_sqlserver())
update.run_taxonomy_update()
