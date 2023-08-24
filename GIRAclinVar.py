# %%
# test change
import numpy
import requests
import pandas
import json
import os
from datetime import datetime as dt

from pathlib import Path

# %%
#from config import api_config as cfg;
from configparser import ConfigParser
config = ConfigParser()
config.read('./config/keys_config.cfg')

R4_API_TOKEN = config.get('redcap', 'R4_api_token')

# %%
### Constants
R4_api_url='https://redcap.vanderbilt.edu/api/'
R4copy_api_url='https://redcap.research.cchmc.org/api/'
USE_SSH = False

record_ids = pandas.read_csv("/Volumes/Emerge_R4/26-JUL-2023 for Shipment 3/UC_27JUL2023/Prowse_MERGEIV_UCMRNs_ship3 2.csv")
record_ids = pandas.DataFrame(record_ids)
record_ids = record_ids.drop(record_ids.index[19:83])
# for UC only
record_ids = record_ids.drop('uc_mrn', axis=1)
record_ids.rename(columns={'record_id1': 'record_id', 'ptlabid': 'participant_lab_id'}, inplace=True)
record_ids = record_ids[['record_id', 'participant_lab_id']].copy()
record_ids = record_ids.astype({"record_id": int})

###

record_ids.rename(columns={'Record ID': 'record_id', 'Participant Lab ID': 'participant_lab_id'},inplace=True)
record_ids = record_ids[['record_id', 'participant_lab_id']].copy()
# record_ids.drop(record_ids[record_ids['record_id'] == 7943].index, inplace = True)

general_info = pandas.read_csv("/Volumes/Emerge_R4/26-JUL-2023 for Shipment 3/UC_27JUL2023/UCHealth_Demo_202307.csv")
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

ICD_flags = pandas.read_csv("/Volumes/Emerge_R4/26-JUL-2023 for Shipment 3/UC_27JUL2023/UCHealth_ICD_flag_first_dx_3yr_202307.csv")
ICD_flags = pandas.DataFrame(ICD_flags)
ICD_flags.columns = map(str.lower, ICD_flags.columns)
ICD_import = pandas.merge(record_ids, ICD_flags, how="inner", on="participant_lab_id")
ICD_import = ICD_import.drop('participant_lab_id', axis=1)
ICD_import = ICD_import.drop('pat_mrn_id', axis=1)
ICD_import.drop(ICD_import[ICD_import['record_id'] == 7943].index, inplace = True)
# ICD_import.drop(ICD_import[ICD_import['record_id'] == 1488].index, inplace = True)
# ICD_import.drop(ICD_import[ICD_import['record_id'] == 1489].index, inplace = True)
#ICD_import = ICD_import.drop('pat_id', axis=1)
ICD_json = ICD_import.to_json(orient='records')

allergy_labs = pandas.read_csv("/Volumes/Emerge_R4/26-JUL-2023 for Shipment 3/UC_27JUL2023/UCHealth_Labs_Allergy_202307.csv")
allergy_labs = pandas.DataFrame(allergy_labs)
allergy_labs.columns = map(str.lower, allergy_labs.columns)
allergy_labs_import = pandas.merge(record_ids, allergy_labs, how="inner", on="participant_lab_id")
allergy_labs_import = allergy_labs_import.drop('participant_lab_id', axis=1)
allergy_labs_import = allergy_labs_import.drop('pat_mrn_id', axis=1)
allergy_labs_import = allergy_labs_import[allergy_labs_import.record_id.notnull()]
allergy_labs_json = allergy_labs_import.to_json(orient='records')

numerical_labs = pandas.read_csv("/Volumes/Emerge_R4/26-JUL-2023 for Shipment 3/UC_27JUL2023/UCHealth_Labs_Numerical_202307.csv")
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
systolic_import.drop(systolic_import[systolic_import['record_id'] == 7943].index, inplace = True)
# systolic_import.drop(systolic_import[systolic_import['record_id'] == 1488].index, inplace = True)
# systolic_import.drop(systolic_import[systolic_import['record_id'] == 1489].index, inplace = True)
###
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

#%% GENERAL section import
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': general_info_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url, data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

#%% ICD Age Flags import
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': ICD_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url, data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

#%% allergy labs import
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': allergy_labs_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url, data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

#%% numerical labs import
# HDL
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': HDL_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url, data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

# cholesterol
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': cholest_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url,data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

# triglyceride
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': triglyc_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url,data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

# A1C
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': A1C_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url,data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

# diastolic blood pressure
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': diastolic_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url,data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))

# systolic blood pressure
fields = {
    'token': R4_API_TOKEN,
    'content': 'record',
    'action': 'import',
    'format': 'json',
    'events': '',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'forceAutoNumber': 'false',
    'data': systolic_json,
    'returnContent': 'count',
    'returnFormat': 'json'
}
r = requests.post(R4_api_url,data=fields, verify=USE_SSH)
print('HTTP Status: ' + str(r.status_code))