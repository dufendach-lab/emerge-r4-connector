# %% [markdown]
# # Import changes from R4

# %%
import numpy
import requests
import pandas
import json
import os
from datetime import datetime, date

from pathlib import Path

# %%
from config import api_config as cfg;

# %%
### Constants
USE_SSH = False
DATA_DIR = "./data/"
GIRA_DIR = "./gira_files/"
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
# R4_short_df1 = R4_fullexport_df.loc[0:200]
# R4_short_df2 = R4_fullexport_df.loc[201:400]
# R4_short_df3 = R4_fullexport_df.loc[401:600]
# R4_short_df4 = R4_fullexport_df.loc[601:800]
# R4_short_df5 = R4_fullexport_df.loc[801:1000]
# R4_short_df6 = R4_fullexport_df.loc[1001:1200]
# R4_short_df7 = R4_fullexport_df.loc[1201:1400]
# R4_short_df8 = R4_fullexport_df.loc[1401:1626]
# R4_short_string1 = R4_short_df1.to_json(orient='records')
# R4_short_string2 = R4_short_df2.to_json(orient='records')
# R4_short_string3 = R4_short_df3.to_json(orient='records')
# R4_short_string4 = R4_short_df4.to_json(orient='records')
# R4_short_string5 = R4_short_df5.to_json(orient='records')
# R4_short_string6 = R4_short_df6.to_json(orient='records')
# R4_short_string7 = R4_short_df7.to_json(orient='records')
# R4_short_string8 = R4_short_df8.to_json(orient='records')

R4_edited_string = R4_fullexport_df.to_json(orient='records')
# %%
### create list of file fields that need to be exported + copied over
file_field_list = ['record_id','pdf_file','broad_import_pdf',
                   'completed_signed_consent', 'metree_import_json_file',
                   'metree_import_png', 'invitae_import_json_file',
                   'invitae_hl7_file', 'invitae_import_pdf']
gira_date_list = ['record_id', 'gira_pdf','date_gira_disclosed', 'date_gira_generated' ]
# %%
### filter export dataframe by the file fields
files_export_df = R4_fullexport_df[file_field_list]
gira_export_df = R4_fullexport_df[gira_field_list]
gira_date_df = R4_fullexport_df[gira_date_list]
concat_gira = gira_date_df.groupby('record_id').agg({'date_gira_generated':'last', 'date_gira_disclosed':'first', 'gira_pdf': 'last'}).reset_index()
concat_gira = concat_gira[concat_gira.date_gira_generated != '']
concat_gira['date_gira_generated'] = pandas.to_datetime(concat_gira['date_gira_generated'])
#concat_gira['date_gira_generated'] = pandas.to_datetime(concat_gira['date_gira_generated']).dt.date
concat_gira['Difference'] = (datetime.today() - concat_gira['date_gira_generated'])
concat_gira["Difference"] = (concat_gira["Difference"]).dt.days
gira_uploads = concat_gira[((concat_gira['Difference'] >= 2) & (concat_gira['date_gira_disclosed'] == '')) | (concat_gira['date_gira_disclosed'] >= last_runtime)]
# %%
### melt file dataframe so record, field, and filename are columns
files_eav = pandas.melt(files_export_df, id_vars=['record_id'], var_name='field', value_name='file_name')
gira_eav = pandas.melt(gira_uploads, id_vars=['record_id'], var_name='field', value_name='file_name')
gira_eav = gira_eav.loc[(gira_eav['field'] == 'gira_pdf')]

# %%
### remove rows that don't have a filename (no file uploaded in R4)
filtered_files_eav = files_eav[files_eav.file_name != '']

# %%
### separate into consent files and non-consent files
consent_files = filtered_files_eav[filtered_files_eav.field == 'completed_signed_consent']

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
gira_files_list = gira_eav.values.tolist()
# %%
### export consent PDF files from R4 to local folder
for ind in consent_files_list:
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
    r = requests.post(cfg.config['R4_api_url'],data=data,verify=USE_SSH, timeout=None)
    print('HTTP Status: ' + str(r.status_code))
    with open(DATA_DIR + str(filename), 'wb') as f:
        f.write(r.content)
        f.close()

# export gira PDF files from R4 to local folder
for gira in gira_files_list:
    record_id = gira[0]
    field = gira[1]
    filename = gira[2]
    data = {
        'token': cfg.config['R4_api_token'],
        'content': 'file',
        'action': 'export',
        'record': record_id,
        'field': field,
        'event': '',
        'returnFormat': 'json'
    }
    r = requests.post(cfg.config['R4_api_url'], data=data, verify=USE_SSH, timeout=None)
    print('HTTP Status: ' + str(r.status_code))
    with open(GIRA_DIR + str(filename), 'wb') as f:
        f.write(r.content)
        f.close()

#%% Convert consent files to HIM-compatible format
### create dataframe of fields for consent files for HIM
him_filename_fields = ['record_id', 'age', 'name_of_participant_part1',
                       'date_consent_cchmc_pp_2', 'date_p2_consent_cchmc',
                       'date_of_birth_child', 'date_of_birth']
him_filename_df = R4_fullexport_df[him_filename_fields]
# him_filename_df = him_filename_df[him_filename_df.name_of_participant_part1 != '']
him_filtered = him_filename_df.loc[(him_filename_df['date_consent_cchmc_pp_2'] != '') | (him_filename_df['date_p2_consent_cchmc'] != '')]
him_filtered = him_filtered.astype({"age": int})

# pull MRN from enrollment tracking REDCap project
data = {
    'token': cfg.config['prows_api_token'],
    'content': 'record',
    'action': 'export',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'fields[0]': 'record_id1',
    'fields[1]': 'mrn',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'true',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json',
    'dateRangeBegin': '2010-01-01 01:00',
    'dateRangeEnd': ''
}

# %%
r = requests.post(cfg.config['prows_api_url'], data=data, verify=USE_SSH, timeout=None, headers=headers)
print('HTTP Status: ' + str(r.status_code))
#
prows_mrn_string = r.content.decode("utf-8")
prows_mrn_dict = json.loads(prows_mrn_string)
prows_mrn_df = pandas.DataFrame(prows_mrn_dict)
prows_mrn_df = prows_mrn_df[prows_mrn_df['mrn'] != '']
prows_mrn_df['record_id1'] = prows_mrn_df['record_id1'].astype('int64')

# create dataframe of fields for GIRA FHIR message
gira_message_fields = ['record_id', 'gira_pdf','name_of_participant_part1', 'date_of_birth_child',
                       'date_of_birth', 'sex_at_birth', 'gira_report_id', 'date_gira_generated', 'age']
gira_message_df = R4_fullexport_df[gira_message_fields]
gira_message_df['record_id'] = gira_message_df['record_id'].astype('int64')
gira_uploads['record_id'] = gira_uploads['record_id'].astype('int64')
gira_message_df['date_gira_generated'] = pandas.to_datetime(gira_message_df['date_gira_generated'])
gira_message_df = gira_message_df.groupby('record_id').agg(
    {'gira_pdf':'last', 'name_of_participant_part1':'first', 'gira_pdf': 'last',
     'date_of_birth_child': 'first', 'date_of_birth': 'first', 'sex_at_birth': 'first',
     'gira_report_id': 'last', 'date_gira_generated': 'last',
     'age': 'first'}).reset_index()
gira_message_df = gira_message_df[gira_message_df['gira_pdf'] != '']

filtered_gira_message = pandas.merge(gira_uploads, gira_message_df, how='left', on=['record_id', 'gira_pdf', 'date_gira_generated'])
final_gira_message = pandas.merge(filtered_gira_message, prows_mrn_df, how='left', left_on='record_id', right_on='record_id1')
gira_message_list = final_gira_message.values.tolist()
# %%
### merge dataframes for HIM file fields + table of consent file exports
him_consent_join = pandas.merge(him_filtered, consent_files, on='record_id')

# %%
### remove whitespace and special characters from participant names
him_consent_join['name_of_participant_part1'] = him_consent_join['name_of_participant_part1'].str.replace('\W', '')

# %%
### reformat dates
him_consent_join['date_consent_cchmc_pp_2'] = pandas.to_datetime(him_consent_join['date_consent_cchmc_pp_2'])
him_consent_join['date_consent_cchmc_pp_2'] = him_consent_join['date_consent_cchmc_pp_2'].dt.strftime("%d%b%Y")
him_consent_join['date_p2_consent_cchmc'] = pandas.to_datetime(him_consent_join['date_p2_consent_cchmc'])
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

him_newnames_df = pandas.DataFrame({'newname': him_newnames_list})
him_consent_join = him_consent_join.join(him_newnames_df)
him_consent_list = him_consent_join.values.tolist()

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


# import required packages
from fhirclient import client
from fhirclient.models import bundle, documentreference, domainresource, encounter, organization, patient, practitioner, reference, resource, observation
import base64
import json
import requests
from urllib import request, parse
# define function for referencing a different resource
def to_reference(res):
    ref_type = res['resourceType']
    ref_id = res['id']
    full_ref = ref_type + "/" + ref_id
    return full_ref


# find PDF file of interest and convert to base64 in a loop
for item in gira_message_list:
    record_id = ind[0]
    giradate = ind[1]
    filename = ind[3]
    name = ind[5]
    age = ind[10]
    mrn = ind[11]
    if age < 18:
        dob = ind[6]
    else:
        dob = ind[7]
    sex = ind[8]
    gira_id = ind[9]
    with open(DATA_DIR + str(filename), 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode('utf-8')
    pat_json = {
        "resourceType": "Patient",
        "identifier": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "MR"
                }]
            },
            "system": "urn:oid:2.16.840.1.113883.3.1674",
            "value": mrn
        }],
        "name": [{
            "use": "official",
            "family": name.split()[1],
            "given": [name.split()[0]]
        }],
        "birthDate": "1974-12-25",
        "gender": sex
    }
    org_hosp_json = {
    "resourceType": "Organization",
    "id": "1702",
    "identifier": [{
        "system": "urn:ietf:rfc:3986",
        "value": "urn:oid:2.16.840.1.113883.3.1674"
    }],
    "type": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                    "code": "prov",
                    "display": "Healthcare Provider"
                }
            ]
        }
    ],
    "name": "Cincinnati Children's Hospital Medical Center"
    }
    org_dept_json = {
    "resourceType": "Organization",
    "id": "1662",
    "identifier": [{
        "system": "urn:oid:2.16.840.1.113883.3.1674",
        "value": "20001408"
    }],
    "type": [{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
            "code": "dept",
            "display": "Hospital Department"
        }]
    }],
    "name": "CCM T1 CLINIC",
    "partOf": {
        "reference": to_reference(org_hosp_json)
    }
    }
    prac_json = {
    "resourceType": "Practitioner",
    "id": "1704",
    "identifier": [{
        "use": "official",
        "system": "http://hl7.org/fhir/sid/us-npi",
        "value": "1558565424"
    }],
    "name": [{
        "family": "Wood",
        "given": ["Sharice"],
        "suffix": ["MD"]
    }]
    }
    enc_json = {
    "resourceType": "Encounter",
    "id": "1705",
    "status": "planned",
    "subject": {
        "reference": to_reference(pat_json)
    },
    "serviceProvider": {
        "reference": to_reference(org_dept_json)
    },
    "class": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB",
        "display": "ambulatory"
    },
    "participant": [{
            "individual": {
                "reference": to_reference(prac_json)
            }
    }]
    }
    docref_json = {
    "resourceType": "DocumentReference",
    "id": gira_id,
    "status": "current",
    "description": "GIRA",
    "type": {
        "coding": [{
            "system": "http://loinc.org",
            "code": "11502-2",
            "display": "Laboratory report"
        },
            {
                "system": "urn:oid:2.16.840.1.113883.3.1674",
                "code": "1000267",
                "display": "External Genetics Report"
            }
        ]
    },
    "subject": {
        "reference": to_reference(pat_json)
    },
    "content": [{
        "attachment": {
            "contentType": "application/pdf",
            "data": base64_message,
            "title": "Genome Informed Risk Assessment"
        }
    }],
    "context": {
        "encounter": [
            {
                "reference": to_reference(enc_json)
            }
        ]
    }
    }
    # define entire bundle constant
    message_json = {
    "resourceType": "Bundle",
    "identifier": {
        "system": "http://cincinnatichildrens.org/emerge/bundle_identifier",
        "value": "GIRAbundle"
    },
    "type": "transaction",
    "entry":
        [
            {"resource": org_hosp_json
             },
            {"resource": org_dept_json
             },
            {"resource": pat_json
             },
            {"resource": prac_json
             },
            {"resource": enc_json
             },
            {"resource": docref_json
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json'
    }
    url = "https://llmirthuat02:40010/fhir/"
    payload = message_json
    r = requests.post(url, headers=headers, data=payload,
                  verify='/Users/casjk8/Documents/llmirthuat02.pem', auth=('eMerge', 'eMerge'))
    print(r.text)
