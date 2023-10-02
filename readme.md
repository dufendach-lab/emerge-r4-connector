# Current code issues
The coordinators often let me know that our local REDCap doesn't have the correct number of completed consent forms that R4 has. r4_sync.py runs every two hours on the Linux VM, so why is it missing/skipping these records? In late September 2023 I changed the script to log the current time/latest runtime at the BEGINNING of the script execution rather than the end so that nothing is missed in between the script starting and finishing. 

Sometimes the manual export from R4, which oftentimes just a few days worth of data, is too large to import with the REDCap API. So, if it's greater than a certain size, I've had to break the payload up into smaller chunks. So far I've been doing this manually. Need to add an "if" loop to direct large data exports to be split into smaller pieces. 

The timestamps available through the REDCap API only specify if a record has been modified at all - the timestamp is not specific to the form or data field that was modified. With consent forms this is simple to address because the dates are collected, but with other fields (including other file fields like Broad reports), there is not a date field to refer to. So, every time I export the records modified since the last runtime, ANY record with ANY modification will send all their files (other than consent). How to filter out these unnecessary exports to improve efficiency?

