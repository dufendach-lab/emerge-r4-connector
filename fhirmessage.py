import fhirclient
from fhirclient import client, models
import json
from fhirclient.models import patient as p
from fhirclient.models import documentreference
from fhirclient.models import bundle

settings = {
  'app_id': 'emerge_gira_app',
  'api_base': 'http://localhost:8080/fhir'
}

smart = client.FHIRClient(settings=settings)

patient = p.Patient.read('1', smart.server)
smart.human_name(patient.name[0])

testBundle = {
  "resourceType": "Bundle",
  "type": "transaction"
}

doc_entry = [
    {
        "resourceType": "DocumentReference",
        "id": "GirsDocumentReferenceExample",
        "status": "current",
        "description": "Test Description",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "11502-2"
                }
            ],
            "text": "Laboratory report"
        },
        "subject": {
            "reference": "Patient/1",
            "identifier": {
                "system": "http://example.org/fhir/mrn",
                "value": "mrn12345"
            }
        },
        "content": [
            {
                "attachment": {
                    "url": "file:///Users/casjk8/Documents/JC_Mar10_Mike.pdf",
                    "title": "SamplePDF"
                }
            }
        ]
    }
    ]

docref = documentreference.DocumentReference(jsondict=doc_entry)
documentreference.DocumentReference.update(docref, smart)
#######
doc_entry2 = {
    "resourceType": "bundle",
    "identifier": "GIRAbundle",
    "type": "transaction",
    "entry" = [
    {
        "resource": {
            "resourceType": "Patient",
            "id": "2",
            "birthDate": "2008-01-06",
            "identifier": [
                {
                    "value": "0000000001",
                    "type": {
                        "text": "MRN"
                    }
                }
            ]
        },
        "request": {
            "method": "POST",
            "url": "Patient",
            "ifNoneExist": "identifier=http://example.org/mrns|12345"
        }
    },
    {
        "resource": {
            "resourceType": "DocumentReference",
            "id": "GirsDocumentReferenceExample",
            "subject": {
                "reference": "Patient/GIRApatient"
            },
            "status": "current",
            "description": "Test Description",
            "type": "11502-2",
            "context": [
                {
                    "reference": "Patient/Encounter"
                }
            ],
            "content": [
                {
                    "attachment": {
                        "url": "file:///Users/casjk8/Documents/JC_Mar10_Mike.pdf",
                        "title": "SamplePDF"
                    }





#             "resource": {
#                 "resourceType": "DocumentReference",
#                 "id": "GirsDocumentReferenceExample",
#                 "subject": {
#                     "reference": "Patient/GIRApatient"
#                 },
#                 "status": "current",
#                 "description": "Test Description",
#                 "type": {
#                     "text": "Laboratory report"
#                 },
#                 "context": [
#                     {
#                         "reference": "Patient/Encounter"
#                     }
#                 ],
#                 "content": [
#                     {
#                         "attachment": {
#                             "url": "file:///Users/casjk8/Documents/JC_Mar10_Mike.pdf",
#                             "title": "SamplePDF"
#                         }
#                     }
#                 ]
#             },
#     "request": {
#         "method": "POST",
#         "url": "DocumentReference"
#     }
# }
# pat_entry =         {
#             "resource": {
#                 "resourceType": "Patient",
#                 "id": "1",
#                 "birthDate": "2008-01-06",
#                 "identifier": [
#                     {
#                         "value": "0000000001",
#                         "type": {
#                             "text": "MR"
#                         }
#                     }
#                 ]
#             },
