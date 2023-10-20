# %%
import sys

import numpy
import requests
import pandas
import json
import os
from datetime import datetime as dt

from pathlib import Path

# %%
from config import api_config as cfg;

# %%
### Constants
R4_api_url='https://redcap.vanderbilt.edu/api/'
R4copy_api_url='https://redcap.research.cchmc.org/api/'
USE_SSH = False

### CCHMC ###
## NEW CODE FOR INTERACTIVITY ##
cchmc_clinvar_path = str(sys.argv[1])
# cchmc_clinvar_path = '/Volumes/Emerge_R4/26-JUL-2023 for Shipment 3'
if os.path.exists(cchmc_clinvar_path):
    print("CCHMC path exists")
else:
    print("Cannot find that folder path")

cchmc_dir_list = os.listdir(cchmc_clinvar_path)
print("Files and directories in '", cchmc_clinvar_path, "' :")
print(cchmc_dir_list)
cchmc_records_key = 'EHRPull'
cchmc_demo_key = 'Demo'
cchmc_icd_key = 'ICD'
cchmc_allergy_key = 'Allergy'
cchmc_num_key = 'Numerical'
for fname in cchmc_dir_list:
    if cchmc_demo_key in fname:
        ccchmc_demo_file = (cchmc_clinvar_path + "/" + fname)
    elif cchmc_icd_key in fname:
        cchmc_icd_file = (cchmc_clinvar_path + "/" + fname)
    elif cchmc_allergy_key in fname:
        cchmc_allergy_file = (cchmc_clinvar_path + "/" + fname)
    elif cchmc_num_key in fname:
        cchmc_num_file = (cchmc_clinvar_path + "/" + fname)
    elif cchmc_records_key in fname:
        cchmc_records_file = (cchmc_clinvar_path + "/" + fname)


### FILES LOCATED IN smb://rds6.cchmc.org/bmi-7/I2B2/Reports/Emerge_R4
record_ids_cchmc = pandas.read_csv(cchmc_records_file)
record_ids_cchmc = pandas.DataFrame(record_ids_cchmc)
# use below line if Python reads in blank 'ids' in the record_id column
record_ids_cchmc = record_ids_cchmc[record_ids_cchmc['record_id1'].notna()]
record_ids_cchmc.rename(columns={'record_id1': 'record_id', 'ptlabid': 'participant_lab_id'}, inplace=True)
record_ids_cchmc = record_ids_cchmc[['record_id', 'participant_lab_id']].copy()
record_ids_cchmc = record_ids_cchmc.astype({"record_id": int})

###
record_ids_cchmc.rename(columns={'Record ID': 'record_id', 'Participant Lab ID': 'participant_lab_id'},inplace=True)
# record_ids.drop(record_ids[record_ids['record_id'] == 7943].index, inplace = True)

cchmc_json_list = []
def reformat_cchmc_demographics(cchmc_demo_file):
    general_info = pandas.read_csv(ccchmc_demo_file)
    general_info = pandas.DataFrame(general_info)
    general_info.columns = map(str.lower, general_info.columns)
    general_info_import = pandas.merge(record_ids, general_info, how="inner", on="participant_lab_id")
    general_info_import = general_info_import.drop(columns=['participant_lab_id'])
    general_info_import.rename(columns={'part_first_name': 'ehr_participant_first_name', 'part_last_name': 'ehr_participant_last_name', 'date_of_birth': 'ehr_date_of_birth'},inplace=True)
    general_info_import['ehr_date_of_birth'] = pandas.to_datetime(general_info_import['ehr_date_of_birth'])
    general_info_import['ehr_date_of_birth'] = general_info_import['ehr_date_of_birth'].dt.strftime('%Y-%m-%d')
    general_info_json = general_info_import.to_json(orient='records')
    cchmc_json_list.append(general_info_json)
    return general_info_json

demographics_cchmc_json = reformat_cchmc_demographics(ccchmc_demo_file)
def reformat_icd(cchmc_icd_file):
    ICD_flags = pandas.read_csv(cchmc_icd_file)
    ICD_flags = pandas.DataFrame(ICD_flags)
    ICD_flags.columns = map(str.lower, ICD_flags.columns)
    ICD_import = pandas.merge(record_ids, ICD_flags, how="inner", on="participant_lab_id")
    ICD_import = ICD_import.drop('participant_lab_id', axis=1)
    # ICD_import = ICD_import.drop('pat_mrn_id', axis=1)
    # ICD_import.drop(ICD_import[ICD_import['record_id'] == 7943].index, inplace = True)
    # ICD_import.drop(ICD_import[ICD_import['record_id'] == 1488].index, inplace = True)
    # ICD_import.drop(ICD_import[ICD_import['record_id'] == 1489].index, inplace = True)
    ICD_json = ICD_import.to_json(orient='records')
    cchmc_json_list.append(ICD_json)
    return ICD_json

ICD_json = reformat_icd(cchmc_icd_file)
def reformat_allergy(cchmc_allergy_file):
    allergy_labs = pandas.read_csv(cchmc_allergy_file)
    allergy_labs = pandas.DataFrame(allergy_labs)
    allergy_labs.columns = map(str.lower, allergy_labs.columns)
    allergy_labs_import = pandas.merge(record_ids, allergy_labs, how="inner", on="participant_lab_id")
    allergy_labs_import = allergy_labs_import.drop('participant_lab_id', axis=1)
    allergy_labs_import = allergy_labs_import.drop('pat_mrn_id', axis=1)
    allergy_labs_import = allergy_labs_import[allergy_labs_import.record_id.notnull()]
    allergy_labs_json = allergy_labs_import.to_json(orient='records')
    cchmc_json_list.append(allergy_json)
    return allergy_json

allergy_json = reformat_allergy(cchmc_allergy_file)
def reformat_numerical(cchmc_num_file):
    numerical_labs = pandas.read_csv(cchmc_num_file)
    numerical_labs = pandas.DataFrame(numerical_labs)
    numerical_labs.columns = map(str.lower, numerical_labs.columns)
    numerical_labs_import = pandas.merge(record_ids, numerical_labs, how="inner", on="participant_lab_id")
    # numerical_labs_import = numerical_labs_import[numerical_labs_import.lab_name.notnull()]
    numerical_labs_import = numerical_labs_import.drop('participant_lab_id', axis=1)
    numerical_labs_import['date_at_event'] = pandas.to_datetime(numerical_labs_import['date_at_event'])
    numerical_labs_import['date_at_event'] = numerical_labs_import['date_at_event'].dt.strftime('%Y-%m-%d')
    # numerical_labs_import = numerical_labs_import.drop('pat_mrn_id', axis=1)
    return numerical_labs_import

numerical_labs_import = reformat_numerical(cchmc_num_file)

def get_systolic(numerical_labs_import):
    systolic_import = numerical_labs_import[numerical_labs_import.lab_name == 'Systolic BP']
    systolic_import.rename(columns={'lab_name': 'sbp_lab_name', 'measurement_concept_id': 'sbp_measurement_concept_id', 'date_at_event': 'sbp_date_at_event', 'value_most_recent': 'sbp_value_most_recent'},inplace=True)
    # WITHDRAWN
    # systolic_import.drop(systolic_import[systolic_import['record_id'] == 7943].index, inplace = True)
    # systolic_import.drop(systolic_import[systolic_import['record_id'] == 1488].index, inplace = True)
    # systolic_import.drop(systolic_import[systolic_import['record_id'] == 1489].index, inplace = True)
    ###
    systolic_json = systolic_import.to_json(orient='records')
    cchmc_json_list.append(systolic_json)
    return systolic_json

systolic_json = get_systolic(numerical_labs_import)
def get_diastolic(numerical_labs_import):
    diastolic_import = numerical_labs_import[numerical_labs_import.lab_name == 'Diastolic BP']
    # WITHDRAWN
    # diastolic_import.drop(diastolic_import[diastolic_import['record_id'] == 7943].index, inplace = True)
    # diastolic_import.drop(diastolic_import[diastolic_import['record_id'] == 1488].index, inplace = True)
    # diastolic_import.drop(diastolic_import[diastolic_import['record_id'] == 1489].index, inplace = True)
    diastolic_import.rename(columns={'lab_name': 'dbp_lab_name', 'measurement_concept_id': 'dbp_measurement_concept_id', 'date_at_event': 'dbp_date_at_event', 'value_most_recent': 'dbp_value_most_recent'},inplace=True)
    diastolic_json = diastolic_import.to_json(orient='records')
    cchmc_json_list.append(diastolic_json)
    return diastolic_json

diastolic_json = get_diastolic(numerical_labs_import)
def get_HDL(numerical_labs_import):
    HDL_import = numerical_labs_import[numerical_labs_import.lab_name == 'HDL']
    # WITHDRAWN
    # HDL_import.drop(HDL_import[HDL_import['record_id'] == 7943].index, inplace = True)
    HDL_import.rename(columns={'lab_name': 'hdl_lab_name', 'measurement_concept_id': 'hdl_measurement_concept_id', 'date_at_event': 'hdl_date_at_event', 'value_most_recent': 'hdl_value_most_recent'},inplace=True)
    HDL_json = HDL_import.to_json(orient='records')
    cchmc_json_list.append(HDL_json)
    return HDL_json

HDL_json = get_HDL(numerical_labs_import)

def get_A1C(numerical_labs_import):
    A1C_import = numerical_labs_import[numerical_labs_import.lab_name == 'A1C']
    # WITHDRAWN
    # A1C_import.drop(A1C_import[A1C_import['record_id'] == 7943].index, inplace = True)
    A1C_import.rename(columns={'lab_name': 'a1c_lab_name', 'measurement_concept_id': 'a1c_measurement_concept_id', 'date_at_event': 'a1c_date_at_event', 'value_most_recent': 'a1c_value_most_recent'},inplace=True)
    A1C_json = A1C_import.to_json(orient='records')
    cchmc_json_list.append(A1C_json)
    return A1C_json

A1C_json = get_A1C(numerical_labs_import)
def get_triglyc(numerical_labs_import):
    triglyc_import = numerical_labs_import[numerical_labs_import.lab_name == 'Triglyceride']
    # WITHDRAWN
    # triglyc_import.drop(triglyc_import[triglyc_import['record_id'] == 778].index, inplace = True)
    triglyc_import.rename(columns={'lab_name': 'triglyceride_lab_name', 'measurement_concept_id': 'triglyceride_measurement_concept_id', 'date_at_event': 'triglyceride_date_at_event', 'value_most_recent': 'triglyceride_value_most_recent'},inplace=True)
    triglyc_json = triglyc_import.to_json(orient='records')
    cchmc_json_list.append(triglyc_json)
    return triglyc_json

triglyc_json = get_triglyc(numerical_labs_import)

def get_cholest(numerical_labs_import):
    cholest_import = numerical_labs_import[numerical_labs_import.lab_name == 'Total Cholesterol']
    # WITHDRAWN
    # cholest_import.drop(cholest_import[cholest_import['record_id'] == 778].index, inplace = True)
    cholest_import.rename(columns={'lab_name': 'totalcholest_lab_name', 'measurement_concept_id': 'totalcholest_measurement_concept_id', 'date_at_event': 'totalcholest_date_at_event', 'value_most_recent': 'totalcholest_value_most_recent'},inplace=True)
    cholest_json = cholest_import.to_json(orient='records')
    cchmc_json_list.append(cholest_json)
    return cholest_json

cholest_json = get_cholest(numerical_labs_import)

for json_upload in cchmc_json_list:
    fields = {
        'token': cfg.config['R4_api_token'],
        'content': 'record',
        'action': 'import',
        'format': 'json',
        'events': '',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'data': json_upload,
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    r = requests.post(R4_api_url, data=fields, verify=USE_SSH)
    print('HTTP Status: ' + str(r.status_code))

### UC ###
## NEW CODE FOR INTERACTIVITY ##
uc_clinvar_path = str(sys.argv[2])
if os.path.exists(uc_clinvar_path):
    print("UC path exists")
else:
    print("Cannot find that folder path")

uc_dir_list = os.listdir(uc_clinvar_path)
print("Files and directories in '", uc_clinvar_path, "' :")
print(uc_dir_list)
uc_records_key = 'Prows'
uc_demo_key = 'Demo'
uc_icd_key = 'ICD'
uc_allergy_key = 'Allergy'
uc_num_key = 'Numerical'
for fname in uc_dir_list:
    if uc_demo_key in fname:
        uc_demo_file = (uc_clinvar_path + "/" + fname)
    elif uc_icd_key in fname:
        uc_icd_file = (uc_clinvar_path + "/" + fname)
    elif uc_allergy_key in fname:
        uc_allergy_file = (uc_clinvar_path + "/" + fname)
    elif uc_num_key in fname:
        uc_num_file = (uc_clinvar_path + "/" + fname)
    elif uc_records_key in fname:
        uc_records_file = (uc_clinvar_path + "/" + fname)


### FILES LOCATED IN smb://rds6.cchmc.org/bmi-7/I2B2/Reports/Emerge_R4
### CHANGE FILEPATH IN LINE BELOW ###
record_ids = pandas.read_csv(uc_records_file)
record_ids = pandas.DataFrame(record_ids)
# use below line if Python reads in blank 'ids' in the record_id column
record_ids = record_ids[record_ids['record_id1'].notna()]
# for UC only
record_ids = record_ids.drop('uc_mrn', axis=1)
record_ids.rename(columns={'record_id1': 'record_id', 'ptlabid': 'participant_lab_id'}, inplace=True)
record_ids = record_ids[['record_id', 'participant_lab_id']].copy()
record_ids = record_ids.astype({"record_id": int})

###
record_ids.rename(columns={'Record ID': 'record_id', 'Participant Lab ID': 'participant_lab_id'},inplace=True)
# record_ids.drop(record_ids[record_ids['record_id'] == 7943].index, inplace = True)

general_info = pandas.read_csv(uc_demo_file)
general_info = pandas.DataFrame(general_info)
general_info.columns = map(str.lower, general_info.columns)
general_info_import = pandas.merge(record_ids, general_info, how="inner", on="participant_lab_id")

# for UC only
general_info_import = general_info_import.drop(columns=['participant_lab_id', 'pat_mrn_id'])
###

general_info_import.rename(columns={'part_first_name': 'ehr_participant_first_name', 'part_last_name': 'ehr_participant_last_name', 'date_of_birth': 'ehr_date_of_birth'},inplace=True)
general_info_import['ehr_date_of_birth'] = pandas.to_datetime(general_info_import['ehr_date_of_birth'])
general_info_import['ehr_date_of_birth'] = general_info_import['ehr_date_of_birth'].dt.strftime('%Y-%m-%d')
general_info_json = general_info_import.to_json(orient='records')

ICD_flags = pandas.read_csv(uc_icd_file)
ICD_flags = pandas.DataFrame(ICD_flags)
ICD_flags.columns = map(str.lower, ICD_flags.columns)
ICD_import = pandas.merge(record_ids, ICD_flags, how="inner", on="participant_lab_id")
ICD_import = ICD_import.drop('participant_lab_id', axis=1)
ICD_import = ICD_import.drop('pat_mrn_id', axis=1)
# ICD_import.drop(ICD_import[ICD_import['record_id'] == 7943].index, inplace = True)
ICD_json = ICD_import.to_json(orient='records')

allergy_labs = pandas.read_csv(uc_allergy_file)
allergy_labs = pandas.DataFrame(allergy_labs)
allergy_labs.columns = map(str.lower, allergy_labs.columns)
allergy_labs_import = pandas.merge(record_ids, allergy_labs, how="inner", on="participant_lab_id")
allergy_labs_import = allergy_labs_import.drop('participant_lab_id', axis=1)
allergy_labs_import = allergy_labs_import.drop('pat_mrn_id', axis=1)
allergy_labs_import = allergy_labs_import[allergy_labs_import.record_id.notnull()]
allergy_labs_json = allergy_labs_import.to_json(orient='records')

numerical_labs = pandas.read_csv(uc_num_file)
numerical_labs = pandas.DataFrame(numerical_labs)
numerical_labs.columns = map(str.lower, numerical_labs.columns)
numerical_labs_import = pandas.merge(record_ids, numerical_labs, how="inner", on="participant_lab_id")
#numerical_labs_import = numerical_labs_import[numerical_labs_import.lab_name.notnull()]
numerical_labs_import = numerical_labs_import.drop('participant_lab_id', axis=1)
numerical_labs_import['date_at_event'] = pandas.to_datetime(numerical_labs_import['date_at_event'])
numerical_labs_import['date_at_event'] = numerical_labs_import['date_at_event'].dt.strftime('%Y-%m-%d')
numerical_labs_import = numerical_labs_import.drop('pat_mrn_id', axis=1)

systolic_import = numerical_labs_import[numerical_labs_import.lab_name == 'Systolic BP']
# WITHDRAWN
# systolic_import.drop(systolic_import[systolic_import['record_id'] == 7943].index, inplace = True)

systolic_import.rename(columns={'lab_name': 'sbp_lab_name', 'measurement_concept_id': 'sbp_measurement_concept_id', 'date_at_event': 'sbp_date_at_event', 'value_most_recent': 'sbp_value_most_recent'},inplace=True)
systolic_json = systolic_import.to_json(orient='records')

diastolic_import = numerical_labs_import[numerical_labs_import.lab_name == 'Diastolic BP']
# WITHDRAWN
diastolic_import.drop(diastolic_import[diastolic_import['record_id'] == 7943].index, inplace = True)
# diastolic_import.drop(diastolic_import[diastolic_import['record_id'] == 1488].index, inplace = True)
# diastolic_import.drop(diastolic_import[diastolic_import['record_id'] == 1489].index, inplace = True)
###
diastolic_import.rename(columns={'lab_name': 'dbp_lab_name', 'measurement_concept_id': 'dbp_measurement_concept_id', 'date_at_event': 'dbp_date_at_event', 'value_most_recent': 'dbp_value_most_recent'},inplace=True)
diastolic_json = diastolic_import.to_json(orient='records')

HDL_import = numerical_labs_import[numerical_labs_import.lab_name == 'HDL']
# WITHDRAWN
HDL_import.drop(HDL_import[HDL_import['record_id'] == 7943].index, inplace = True)
###
HDL_import.rename(columns={'lab_name': 'hdl_lab_name', 'measurement_concept_id': 'hdl_measurement_concept_id', 'date_at_event': 'hdl_date_at_event', 'value_most_recent': 'hdl_value_most_recent'},inplace=True)
HDL_json = HDL_import.to_json(orient='records')

A1C_import = numerical_labs_import[numerical_labs_import.lab_name == 'A1C']
# WITHDRAWN
A1C_import.drop(A1C_import[A1C_import['record_id'] == 7943].index, inplace = True)
###
A1C_import.rename(columns={'lab_name': 'a1c_lab_name', 'measurement_concept_id': 'a1c_measurement_concept_id', 'date_at_event': 'a1c_date_at_event', 'value_most_recent': 'a1c_value_most_recent'},inplace=True)
A1C_json = A1C_import.to_json(orient='records')

triglyc_import = numerical_labs_import[numerical_labs_import.lab_name == 'Triglyceride']
# WITHDRAWN
triglyc_import.drop(triglyc_import[triglyc_import['record_id'] == 778].index, inplace = True)
###
triglyc_import.rename(columns={'lab_name': 'triglyceride_lab_name', 'measurement_concept_id': 'triglyceride_measurement_concept_id', 'date_at_event': 'triglyceride_date_at_event', 'value_most_recent': 'triglyceride_value_most_recent'},inplace=True)
triglyc_json = triglyc_import.to_json(orient='records')

cholest_import = numerical_labs_import[numerical_labs_import.lab_name == 'Total Cholesterol']
# WITHDRAWN
# cholest_import.drop(cholest_import[cholest_import['record_id'] == 778].index, inplace = True)
###
cholest_import.rename(columns={'lab_name': 'totalcholest_lab_name', 'measurement_concept_id': 'totalcholest_measurement_concept_id', 'date_at_event': 'totalcholest_date_at_event', 'value_most_recent': 'totalcholest_value_most_recent'},inplace=True)
cholest_json = cholest_import.to_json(orient='records')



