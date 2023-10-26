import numpy
import requests
import pandas
import json
import os
from datetime import datetime, timedelta
import base64
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

def get_last_runtime():
    last_run_file = Path('./run_history.log')
    last_run_file.touch(exist_ok=True)
    num_lines = sum(1 for _ in open(last_run_file))
    if num_lines < 1:
        last_runtime = '2000-01-01 01:01'
    else:
        with open(last_run_file, 'r') as f:
            last_runtime = f.readlines()[-1]
    return last_runtime

last_time = get_last_runtime()
print("last runtime:", last_time)
diff = pandas.to_datetime(last_time) - timedelta(days=1)
diff = diff.strftime('%Y-%m-%d')
new_lasttime = str(diff)
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


new_runtime = print_time()
# %%
def r4_pull(time):
    data = {
        'token': cfg.config['test_project_token'],
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
        'dateRangeBegin': time,
        'dateRangeEnd': ''
    }
    print('r4_pull')
    r4_pull_r = requests.post(cfg.config['test_project_url'],data=data, verify=USE_SSH, timeout=None)
    print('HTTP Status: ' + str(r4_pull_r.status_code))
    return r4_pull_r


r4_pull_r = r4_pull(last_time)

record_count = len(r4_pull_r.json())
print('Records to update: ' + str(record_count))
print(print_time())
if (record_count < 1):
    print('No records to update, quitting script')
    quit()

# %%
def save_r4_export(export):
    R4_fullexport_string = r4_pull_r.content.decode("utf-8")
    R4_fullexport_dict = json.loads(R4_fullexport_string)
    R4_fullexport_df = pandas.DataFrame(R4_fullexport_dict)
    R4_fullexport_df = R4_fullexport_df.loc[:, ~R4_fullexport_df.columns.str.contains('timestamp')]
    return R4_fullexport_df

R4_fullexport_df = save_r4_export(r4_pull_r)
R4_edited_string = R4_fullexport_df.to_json(orient='records')

def get_gira_export_fields():
    gira_date_list = ['record_id', 'gira_pdf','date_gira_disclosed', 'date_gira_generated' ]
    gira_date_df = R4_fullexport_df[gira_date_list]
    concat_gira = gira_date_df.groupby('record_id').agg({'date_gira_generated':'last', 'date_gira_disclosed':'first', 'gira_pdf': 'last'}).reset_index()
    concat_gira = concat_gira[concat_gira.date_gira_generated != '']
    concat_gira['date_gira_generated'] = pandas.to_datetime(concat_gira['date_gira_generated'])
    #concat_gira['date_gira_generated'] = pandas.to_datetime(concat_gira['date_gira_generated']).dt.date
    concat_gira['Difference'] = (datetime.today() - concat_gira['date_gira_generated'])
    concat_gira["Difference"] = (concat_gira["Difference"]).dt.days
    gira_uploads = concat_gira[((concat_gira['Difference'] >= 28) & (concat_gira['date_gira_disclosed'] == '')) | (concat_gira['date_gira_disclosed'] >= last_time)]
    return gira_uploads


gira_uploads = get_gira_export_fields()
gira_eav = pandas.melt(gira_uploads, id_vars=['record_id'], var_name='field', value_name='file_name')
gira_eav = gira_eav.loc[(gira_eav['field'] == 'gira_pdf')]
gira_files_list = gira_eav.values.tolist()

def export_gira_files(gira_files_list):
    for gira in gira_files_list:
        record_id = gira[0]
        field = gira[1]
        filename = gira[2]
        data = {
            'token': cfg.config['test_project_token'],
            'content': 'file',
            'action': 'export',
            'record': record_id,
            'field': field,
            'event': '',
            'returnFormat': 'json'
        }
        print('export_gira_files')
        r = requests.post(cfg.config['test_project_url'], data=data, verify=USE_SSH, timeout=None)
        print('HTTP Status: ' + str(r.status_code))
        with open(GIRA_DIR + str(filename), 'wb') as f:
            f.write(r.content)
            f.close()


export_gira_files(gira_files_list)

def get_mrns():
    data = {
        'token': cfg.config['test_project_token'],
        'content': 'record',
        'action': 'export',
        'format': 'json',
        'type': 'flat',
        'csvDelimiter': '',
        'fields[0]': 'record_id',
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
    print('get_mrns')
    r = requests.post(cfg.config['test_project_url'], data=data, verify=USE_SSH, timeout=None, headers=headers)
    print('HTTP Status: ' + str(r.status_code))
    prows_mrn_string = r.content.decode("utf-8")
    prows_mrn_dict = json.loads(prows_mrn_string)
    prows_mrn_df = pandas.DataFrame(prows_mrn_dict)
    prows_mrn_df = prows_mrn_df[prows_mrn_df['mrn'] != '']
    #prows_mrn_df['record_id'] = prows_mrn_df['record_id'].astype('int64')
    return prows_mrn_df


prows_mrn_df = get_mrns()

def get_gira_message_fields():
    gira_message_fields = ['record_id', 'gira_pdf','name_of_participant_part1', 'date_of_birth_child',
                           'date_of_birth', 'sex_at_birth', 'gira_report_id', 'date_gira_generated', 'age']
    gira_message_df = R4_fullexport_df[gira_message_fields]
    gira_message_df['sex_at_birth'].replace('1', 'female', inplace=True)
    gira_message_df['sex_at_birth'].replace('2', 'male', inplace=True)
    #gira_message_df['record_id'] = gira_message_df['record_id'].astype('int64')
    #gira_uploads['record_id'] = gira_uploads['record_id'].astype('int64')
    gira_message_df['date_gira_generated'] = pandas.to_datetime(gira_message_df['date_gira_generated'])
    gira_message_df = gira_message_df.groupby('record_id').agg(
        {'gira_pdf':'last', 'name_of_participant_part1':'first', 'gira_pdf': 'last',
         'date_of_birth_child': 'first', 'date_of_birth': 'first', 'sex_at_birth': 'first',
         'gira_report_id': 'last', 'date_gira_generated': 'last',
         'age': 'first'}).reset_index()
    gira_message_df = gira_message_df[gira_message_df['gira_pdf'] != '']
    filtered_gira_message = pandas.merge(gira_uploads, gira_message_df, how='left', on=['record_id', 'gira_pdf', 'date_gira_generated'])
    final_gira_message = pandas.merge(filtered_gira_message, prows_mrn_df, how='left', left_on='record_id', right_on='record_id')
    gira_message_list = final_gira_message.values.tolist()
    return gira_message_list


gira_message_list = get_gira_message_fields()

# define function for referencing a different resource

def to_reference(res):
    ref_type = res['resourceType']
    ref_id = res['id']
    full_ref = ref_type + "/" + str(ref_id)
    return full_ref


# find PDF file of interest, convert to base64, create gira message
def create_gira_message(gira_message_list):
    for ind in gira_message_list:
        record_id = ind[0]
        giradate = ind[1]
        filename = ind[3]
        name = ind[5]
        age = ind[10]
        mrn = ind[14]
        if int(age) < 18:
            dob = ind[6]
        else:
            dob = ind[7]
        sex = ind[8]
        gira_id = ind[9]
        with open(GIRA_DIR + str(filename), 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_message = base64_encoded_data.decode('utf-8')
        pat_json = {
            "resourceType": "Patient",
            "id": record_id,
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
            "birthDate": dob,
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
            "date": giradate,
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
                    "data": 'test message',
                    #data": base64_message,
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
        #print(message_json)
        headers = {
           'Content-Type': 'application/json'
        }
        url = "https://interfaceuat:40010/fhir/"
        payload = message_json
        r = requests.post(url, headers=headers, data=payload,
                          verify='/Users/casjk8/Downloads/emerge.mirth.fhir.hl7.cer', auth=('eMerge', 'eMerge'))
        print(r.text)


create_gira_message(gira_message_list)