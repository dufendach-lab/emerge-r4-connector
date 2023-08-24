# import required packages
from fhirclient import client
from fhirclient.models import bundle, documentreference, domainresource, encounter, organization, patient, practitioner, reference, resource, observation
import base64
import json
import requests
from urllib import request, parse

# find PDF file of interest and convert to base64
with open('/Users/casjk8/Documents/sample_site_positiveGIRA.pdf', 'rb') as binary_file:
    binary_file_data = binary_file.read()
    base64_encoded_data = base64.b64encode(binary_file_data)
    base64_message = base64_encoded_data.decode('utf-8')


# define function for referencing a different resource
def to_reference(res):
    ref_type = res['resourceType']
    ref_id = res['id']
    full_ref = ref_type + "/" + ref_id
    return full_ref

# create resource constants
pat_json = {
    "resourceType": "Patient",
    "id": "1703",
    "identifier": [{
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                "code": "MR"
            }]
        },
        "system": "urn:oid:2.16.840.1.113883.3.1674",
        "value": "mrn010101"
    }],
    "name": [{
        "use": "official",
        "family": "last_name",
        "given": ["first_name"]
    }],
    "birthDate": "1974-12-25",
    "gender": "male"
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
    "id": "1706",
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
            "data": decoded_string,
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
