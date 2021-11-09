## Shotgrid Leecher change Log


### [0.0.5] Project data propagation
#### Nov ?? - 2021
 - Add shotgrid step mapping for shot names
#### Nov 08 - 2021
 - Propagate project data (fps, tool env, aspect ratio, etc) to all its descendants throughout the hierarchy
 - Wire up shotgrid project code with its avalon alternative
### [0.0.4] New Batch API
#### Oct 27 - 2021
 - Check Batch API now return the Shotgrid project name when valid
 - The Batch API now returns an error 500 if the Openpype project name and the Shotgrid project name differs
 - Improve batches logs and related APIs
 - Add projects/queue/logs GET endpoints with simple sort/limit/filter abilities
 - Make REST APIs more UI friendlies
 - Few minor fixes

### [0.0.3] Batches scheduling
#### Oct 21 - 2021
 - Add a possibility to schedule batches and execute them in the background
 - Add appropriated REST endpoints
 - Add processing logs

### [0.0.2] Fields mapping and Shot cut data
#### Oct 7 - 2021
 - Add an ability to map names of SG entities fields from one batch to another using `fields_mapping` variable.
 - Add extraction, ingestion and mapping of cut data information at the SG Shots level.

### [0.0.1] Initial release
#### Sep 30 - 2021
