# %% [markdown]
# # Import changes from R4

# %%
import numpy
import requests
import pandas
import json
import os
from datetime import datetime

from pathlib import Path

# %%
from config import api_config as cfg;

# %%
### Constants
USE_SSH = False
DATA_DIR = "./data/"
headers = requests.utils.default_headers()
headers.update(
    {
        'User-Agent': 'My User Agent 1.0',
    }
)

### Get last run time from date file
last_run_file = Path('./run_history.log')
last_run_file.touch(exist_ok=True)

num_lines = sum(1 for _ in open(last_run_file))

if num_lines < 1:
    last_runtime = '2000-01-01 01:01'
else:
    with open(last_run_file, 'r') as f:
        last_runtime = f.readlines()[-1]

print("last runtime:", last_runtime)
# %%
### EXPORT existing records from R4/source REDCap
data = {
    'token': cfg.config['R4_api_token'],
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'forms[0]': 'prescreening_survey',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'true',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json',
    'dateRangeBegin': '2010-01-01 00:00:00',
    'dateRangeEnd': ''
}

# %%
r = requests.post(cfg.config['R4_api_url'], data=data, verify=USE_SSH, timeout=None, headers=headers)
print('HTTP Status: ' + str(r.status_code))

# %%
### store data from request
R4_exportIDs_string = r.content.decode("utf-8")
R4_exportIDs_dict = json.loads(R4_exportIDs_string)
R4_exportIDs_df = pandas.DataFrame(R4_exportIDs_dict)
R4_exportIDs = R4_exportIDs_df['record_id'].tolist()

# %%
### export records from local REDCap for comparison
data = {
    'token': cfg.config['R4copy_api_token'],
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'forms[0]': 'prescreening_survey',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'true',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json',
    'dateRangeBegin': '2000-01-01 00:00:00',
    'dateRangeEnd': ''
}

# %%
r = requests.post(cfg.config['R4copy_api_url'], data=data, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

# %%
### store data from request
R4copy_exportIDs_string = r.content.decode("utf-8")
R4copy_exportIDs_dict = json.loads(R4copy_exportIDs_string)
R4copy_exportIDs_df = pandas.DataFrame(R4copy_exportIDs_dict)
R4copy_exportIDs = R4copy_exportIDs_df['record_id'].tolist()
# R4copy_exportIDs = pandas.DataFrame(R4copy_exportIDs, columns=['record_id'])

# %%
### calculate differences in IDs between projects
add_to_R4copy = list(set(R4_exportIDs) - set(R4copy_exportIDs))
num_add = len(add_to_R4copy)
add_to_R4copy = pandas.DataFrame(add_to_R4copy, columns=['record_id'])
add_to_R4copy = add_to_R4copy.to_json(orient="index")
delete_from_R4copy = list(set(R4copy_exportIDs) - set(R4_exportIDs))
num_delete = len(delete_from_R4copy)
delete_from_R4copy = numpy.asarray(delete_from_R4copy)

# %%
if num_add > 0:
    fields = {
        'token': cfg.config['R4copy_api_token'],
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'events': '',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'data': add_to_R4copy,
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    r = requests.post(cfg.config['R4copy_api_url'], data=fields)
    print('HTTP Status: ' + str(r.status_code))

if num_delete > 0:
    fields = {
        'token': cfg.config['R4copy_api_token'],
        'action': 'delete',
        'content': 'record',
        'records[]': delete_from_R4copy,
        'returnFormat': 'json'
    }
    r = requests.post(cfg.config['R4copy_api_url'], data=fields)
    print('HTTP Status: ' + str(r.status_code))

# %%
def print_time():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M")
    data = current_time
    return data

def write_file(filename,data):
    if os.path.isfile(filename):
        with open (filename, 'a') as f:
            f.write('\n' + data)
    else:
        with open(filename, 'w') as f:
            f.write(data)

write_file('run_history.log', print_time())

# %%
data = {
    'token': cfg.config['R4_api_token'],
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'forms[0]': 'prescreening_survey',
    'forms[1]': 'transition_page',
    'forms[2]': 'primary_consent',
    'forms[3]': 'cchmc_consent_part_2',
    'forms[4]': 'cchmc_consent_parent_permission',
    'forms[5]': 'end_of_consent_transition',
    'forms[6]': 'baseline_survey_adult',
    'forms[7]': 'baseline_survey_child',
    'forms[8]': 'pre_ror_adult',
    'forms[9]': 'pre_ror_child',
    'forms[10]': 'pre_ror_transition',
    'forms[11]': 'adverse_events',
    'forms[12]': 'study_withdrawal',
    'forms[13]': 'consent_upload',
    'forms[14]': 'notes',
    'forms[15]': 'mono_sample',
    'forms[16]': 'broad_ordering',
    'forms[17]': 'metree_import',
    'forms[18]': 'family_relationships',
    'forms[19]': 'completed_signed_consent',
    'forms[20]': 'admin_form',
    'forms[22]': 'unified_variables',
    'forms[23]': 'r4_metree_result',
    'forms[24]': 'r4_invitae_result',
    'forms[25]': 'r4_broad_result',
    'forms[26]': 'gira_clinical_variables',
    'forms[27]': 'invitae_import',
    'forms[28]': 'module_variables',
    'forms[29]': 'gira_review',
    'forms[30]': 'staged_gira',
    'forms[31]': 'gira_reports',
    'forms[32]': 'ror',
    'forms[33]': 'postror_child',
    'forms[34]': 'postror_adult',
    'forms[35]': 'adult_fhh_rescue',
    'forms[36]': 'pediatric_fhh_rescue',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'true',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json',
    'dateRangeBegin': last_runtime,
    'dateRangeEnd': ''
}

# %%
r = requests.post(cfg.config['R4_api_url'],data=data, verify=USE_SSH, timeout=None)
print('HTTP Status: ' + str(r.status_code))

# %%
### Check the record count. If nothing to be updated, quit the script.

record_count = len(r.json())
print('Records to update: ' + str(record_count))
print(print_time())
if (record_count < 1):
    print('No records to update, quitting script')
    quit()

# %%
### Save the content of the request in a data frame.
R4_fullexport_string = r.content.decode("utf-8")
R4_fullexport_dict = json.loads(R4_fullexport_string)
R4_fullexport_df = pandas.DataFrame(R4_fullexport_dict)
R4_fullexport_df = R4_fullexport_df.loc[:, ~R4_fullexport_df.columns.str.contains('timestamp')]
#R4_short_df1 = R4_fullexport_df.loc[0:200]
#R4_short_df2 = R4_fullexport_df.loc[201:400]
#R4_short_df3 = R4_fullexport_df.loc[401:600]
#R4_short_df4 = R4_fullexport_df.loc[601:800]
#R4_short_df5 = R4_fullexport_df.loc[801:1000]
#R4_short_df6 = R4_fullexport_df.loc[1001:1200]
#R4_short_df7 = R4_fullexport_df.loc[1201:1400]
#R4_short_df8 = R4_fullexport_df.loc[1401:1913]
#R4_short_string1 = R4_short_df1.to_json(orient='records')
#R4_short_string2 = R4_short_df2.to_json(orient='records')
#R4_short_string3 = R4_short_df3.to_json(orient='records')
#R4_short_string4 = R4_short_df4.to_json(orient='records')
#R4_short_string5 = R4_short_df5.to_json(orient='records')
#R4_short_string6 = R4_short_df6.to_json(orient='records')
#R4_short_string7 = R4_short_df7.to_json(orient='records')
#R4_short_string8 = R4_short_df8.to_json(orient='records')

R4_edited_string = R4_fullexport_df.to_json(orient='records')
# %%
### create list of file fields that need to be exported + copied over
file_field_list = ['record_id','pdf_file','broad_import_pdf',
                   'completed_signed_consent', 'metree_import_json_file',
                   'metree_import_png', 'invitae_import_json_file',
                   'invitae_hl7_file', 'invitae_import_pdf']

# %%
### filter export dataframe by the file fields
files_export_df = R4_fullexport_df[file_field_list]

# %%
### melt file dataframe so record, field, and filename are columns
files_eav = pandas.melt(files_export_df, id_vars=['record_id'], var_name='field', value_name='file_name')

# %%
### remove rows that don't have a filename (no file uploaded in R4)
filtered_files_eav = files_eav[files_eav.file_name != '']

# %%
### separate into consent files and non-consent files
consent_files = filtered_files_eav[filtered_files_eav.field == 'completed_signed_consent']
nonconsent_files = filtered_files_eav[filtered_files_eav.field != 'completed_signed_consent']

# %%
### convert EAV to a list that the "for" loop below can iterate through
consent_files_list = consent_files.values.tolist()
nonconsent_files_list = nonconsent_files.values.tolist()

# %%
### export consent PDF files from R4 to local folder
# for ind in consent_files_list:
#     record_id = ind[0]
#     field = ind[1]
#     filename = ind[2]
#     data = {
#         'token': cfg.config['R4_api_token'],
#         'content': 'file',
#         'action': 'export',
#         'record': record_id,
#         'field': field,
#         'event': '',
#         'returnFormat': 'json'
#         }
#     r = requests.post(cfg.config['R4_api_url'],data=data,verify=USE_SSH, timeout=None)
#     print('HTTP Status: ' + str(r.status_code))
#     with open(DATA_DIR + str(filename), 'wb') as f:
#         f.write(r.content)
#         f.close()

#%% Convert consent files to HIM-compatible format
### create dataframe of fields for consent files for HIM
him_filename_fields = ['record_id', 'age', 'name_of_participant_part1',
                       'date_consent_cchmc_pp_2', 'date_p2_consent_cchmc',
                       'date_of_birth_child', 'date_of_birth']
him_filename_df = R4_fullexport_df[him_filename_fields]
# him_filename_df = him_filename_df[him_filename_df.name_of_participant_part1 != '']
him_filtered = him_filename_df.loc[(him_filename_df['date_consent_cchmc_pp_2'] != '') | (him_filename_df['date_p2_consent_cchmc'] != '')]
him_filtered = him_filtered.astype({"age": int})

# %%
### merge dataframes for HIM file fields + table of consent file exports
him_consent_join = pandas.merge(him_filtered, consent_files, on='record_id')
### remove whitespace and special characters from participant names
him_consent_join['name_of_participant_part1'] = him_consent_join['name_of_participant_part1'].str.replace('\W', '')
him_lasttime = pandas.to_datetime(last_runtime)
him_lasttime = him_lasttime.replace(hour=0, minute=0, second=0)
him_consent_join['date_consent_cchmc_pp_2'] = pandas.to_datetime(him_consent_join['date_consent_cchmc_pp_2'])
him_consent_join['date_p2_consent_cchmc'] = pandas.to_datetime(him_consent_join['date_p2_consent_cchmc'])
him_consent_join = him_consent_join.loc[(him_consent_join['date_consent_cchmc_pp_2'] >= last_runtime) | (him_consent_join['date_p2_consent_cchmc'] >= last_runtime)]
him_consent_first_list = him_consent_join.values.tolist()

for ind in him_consent_first_list:
    record_id = ind[0]
    field = ind[7]
    filename = ind[8]
    data = {
        'token': cfg.config['R4_api_token'],
        'content': 'file',
        'action': 'export',
        'record': record_id,
        'field': field,
        'event': '',
        'returnFormat': 'json'
        }
    r = requests.post(cfg.config['R4_api_url'],data=data,verify=USE_SSH, timeout=None)
    print('HTTP Status: ' + str(r.status_code))
    with open(DATA_DIR + str(filename), 'wb') as f:
        f.write(r.content)
        f.close()
# %%

# %%
### reformat dates
him_consent_join['date_consent_cchmc_pp_2'] = him_consent_join['date_consent_cchmc_pp_2'].dt.strftime("%d%b%Y")
him_consent_join['date_p2_consent_cchmc'] = him_consent_join['date_p2_consent_cchmc'].dt.strftime("%d%b%Y")
him_consent_join['date_of_birth_child'] = pandas.to_datetime(him_consent_join['date_of_birth_child'])
him_consent_join['date_of_birth_child'] = him_consent_join['date_of_birth_child'].dt.strftime("%d%b%Y")
him_consent_join['date_of_birth'] = pandas.to_datetime(him_consent_join['date_of_birth'])
him_consent_join['date_of_birth'] = him_consent_join['date_of_birth'].dt.strftime("%d%b%Y")

# %%
### convert to list
him_consent_list = him_consent_join.values.tolist()

# %%
## iterate through old file names and rename, add new names to blank list
him_newnames_list = []
him_ids_list = []
for ind in him_consent_list:
    oldfilename = ind[8]
    record_id = ind[0]
    age = ind[1]
    name = ind[2]
    if age < 18:
        sign_date = ind[3]
        dob = ind[5]
    else:
        sign_date = ind[4]
        dob = ind[6]
    newname = str(sign_date)+"_"+str(name)+"_"+str(dob)+".pdf"
    os.rename(DATA_DIR + str(oldfilename), DATA_DIR + str(newname))
    him_newnames_list.append(newname)
    him_ids_list.append(record_id)

him_newnames_df = pandas.DataFrame({'record_id': him_ids_list, 'newname': him_newnames_list})
#him_consent_join = him_consent_join.reset_index(drop=True)
him_consent_join2 = pandas.merge(him_consent_join, him_newnames_df, on='record_id', how='outer')
him_consent_list = him_consent_join2.values.tolist()

# %%
### import renamed consent files into copy of R4
for ind in him_consent_list:
    filename = ind[9]
    data = {
        'token': cfg.config['R4copy_api_token'],
        'content': 'file',
        'action': 'import',
        'record': ind[0],
        'field': ind[7],
        'event': '',
        'returnFormat': 'json'
        }
    with open((DATA_DIR + str(filename)), 'rb') as f:
        r=requests.post(cfg.config['R4copy_api_url'], data=data, files={'file':f}, timeout=None)
        f.close()
        print('HTTP Status: ' + str(r.status_code))

# %%
### export non-consent PDF files from R4 to local folder
for ind in nonconsent_files_list:
    record_id = ind[0]
    field = ind[1]
    filename = ind[2]
    data = {
        'token': cfg.config['R4_api_token'],
        'content': 'file',
        'action': 'export',
        'record': record_id,
        'field': field,
        'event': '',
        'returnFormat': 'json'
        }
    r = requests.post(cfg.config['R4_api_url'],data=data,verify=False, timeout=None)
    print('HTTP Status: ' + str(r.status_code))
    with open(DATA_DIR + str(filename), 'wb') as f:
        f.write(r.content)
        f.close()

# %%
### import non-consent files into copy of R4
for ind in nonconsent_files_list:
    filename = ind[2]
    data = {
        'token': cfg.config['R4copy_api_token'],
        'content': 'file',
        'action': 'import',
        'record': ind[0],
        'field': ind[1],
        'event': '',
        'returnFormat': 'json'
        }
    with open((DATA_DIR + str(filename)), 'rb') as f:
        r=requests.post(cfg.config['R4copy_api_url'], data=data, files={'file':f}, verify=USE_SSH, timeout=None)
        f.close()
        print('HTTP Status: ' + str(r.status_code))

# %%
### empty the data folder
for pdf in os.listdir(DATA_DIR):
    os.remove(os.path.join(DATA_DIR, pdf))

### IMPORT field data into local REDCap
fields = {
    'token': cfg.config['R4copy_api_token'],
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': R4_edited_string,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(cfg.config['R4copy_api_url'],data=fields, verify=USE_SSH, timeout=None)
print('HTTP Status: ' + str(r.status_code))
print(str(r.content))

#%% Update date file with latest run time


# find differences between R4 and copy records
list(set(R4_exportIDs) - set(R4copy_exportIDs))
