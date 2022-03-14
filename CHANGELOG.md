## Shotgrid Leecher change Log

### [0.1.0] Add user/project links API with synchronization
#### March 14 - 2022
  - Add user API and related ingestion mechanisms
  - Add scheduled user/project synchronization
  - Add project/user links rest API 

### [0.0.10] Support custom frame start/end fields
#### March 09 - 2022
  - Add custom frame start/end fields
  - Add app ability to swap environments
### [0.0.9] Split UI and API parts
#### Feb 14 - 2022
  - Add UI management application
  - Enable CORS at API level
### [0.0.8] Propagate shotgrid status to the avalon
#### Jan 27 - 2022
  - Propagate shotgrid status from assets and shots to the avalon assets
### [0.0.7] Manage Assets without type
#### Jan 17 - 2022
  - Attach untyped assets to the project root
  - Add assigned users and status fields to the avalon tasks
### [0.0.6] Improve input links/linked assets
#### Dec 17 - 2021
 - Make avalon object ids be unique and stable, based on shotgrid ids
 - Ingest more entities connection types
 - Add quantity field for all supported connection types
### [0.0.5] Project data propagation
#### Nov 17 - 2021
 - Add support of linked assets at the APIs end
 - Make batch overwrite more softy regarding avalon project
#### Nov 12 - 2021
 - Add shotgrid step mapping for shot names within project config
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
