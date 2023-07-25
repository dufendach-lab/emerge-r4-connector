#Imports
import fhirclient.models.patient
from fhirpy import SyncFHIRClient
from fhir.resources.bundle import Bundle
from fhirclient.models import patient, organization, encounter, bundle, domainresource, reference, practitioner, documentreference
import json
import base64

# personal test HAPI FHIR server
client = SyncFHIRClient(url='http://localhost:8080/fhir')

# endpoint from Sai
client = SyncFHIRClient(url='https://llmirthuat02:40010/fhir/')

# find PDF file of interest and convert to base64
with open("/Users/casjk8/Documents/testBase64.pdf", "rb") as pdf_file:
    encoded_string = base64.b64encode(pdf_file.read())
    encoded_string = str(encoded_string)

# def to_reference(res: domainresource.DomainResource):
#     ref = reference.Reference()
#     ref.reference = res.resource_type + "/" + res.id
#     return ref.reference


def to_reference(res):
    ref_type = res['resourceType']
    ref_id = res['id']
    full_ref = ref_type + "/" + ref_id
    return full_ref


# create constants
pat_const = {
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
    }]
}

org_hosp_const = {
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

org_dept_const = {
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
        "reference": to_reference(org_hosp_const)
    }
}

prac_const = {
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

enc_const = {
    "resourceType": "Encounter",
    "id": "1705",
    "status": "planned",
    "subject": {
        "reference": to_reference(pat_const)
    },
    "serviceProvider": {
        "reference": to_reference(org_dept_const)
    },
    "class": [{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory"
        }]
    }],
    "participant": [{
            "actor": {
                "reference": to_reference(prac_const)
            }
    }]
}


docref_const = {
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
        "reference": to_reference(pat_const)
    },
    "content": [{
        "attachment": {
            "contentType": "application/pdf",
            "data": encoded_string,
            "title": "Genome Informed Risk Assessment"
        }
    }],
    "context": [{
        "reference": to_reference(enc_const)
    }]
}

# entire raw message
message_const = bundle.Bundle({
    "resourceType": "Bundle",
    "identifier": {
        "system": "http://cincinnatichildrens.org/emerge/bundle_identifier",
        "value": "GIRAbundle"
    },
    "type": "transaction",
    "entry":
        [
            {"resource": org_hosp_const,
             "request": {
                 "method": "POST",
                 "url": "Organization"
             }
             },
            {"resource": org_dept_const,
             "request": {
                 "method": "POST",
                 "url": "Organization"
             }
             },
            {"resource": pat_const,
             "request": {
                 "method": "POST",
                 "url": "Patient"
             }
             },
            {"resource": enc_const,
             "request": {
                 "method": "POST",
                 "url": "Encounter"
             }
             },
            {"resource": docref_const,
             "request": {
                 "method": "POST",
                 "url": "DocumentReference"
             }
            }
        ]
})

entry_list = [
    {"resource": org_hosp_const,
     "request": {
         "method": "POST",
         "url": "Organization"
     }
     },
    {"resource": org_dept_const,
     "request": {
         "method": "POST",
         "url": "Organization"
     }
     },
    {"resource": pat_const,
     "request": {
         "method": "POST",
         "url": "Patient"
     }
     },
    {"resource": enc_const,
     "request": {
         "method": "POST",
         "url": "Encounter"
     }
     },
    {"resource": docref_const,
     "request": {
         "method": "POST",
         "url": "DocumentReference"
     }
     }
]

# fhirpy version
bundle0 = Bundle(type="transaction")

# entrylist = [
#     {
#         "resource": {
#             "resourceType": "Organization",
#             "id": "33",
#             "identifier": [{
#                 "system": "http://testOrganization.org",
#                 "value": "20001408"
#             }],
#         },
#         "request": {
#             "method": "POST",
#             "url": "Organization"
#         }
#     },
    # {"resource": {
    #     "resourceType": "Patient",
    #     "birthDate": "2010-01-01",
    #     "identifier": [{
    #         "value": "mrn010101",
    #         "system": "http://testPatient.org"
    #     }],
    # },
    #     "request": {
    #         "method": "POST",
    #         "url": "Patient"
    #     }
    # },
    # {"resource": {
    #     "resourceType": "Patient",
    #     "birthDate": "2010-01-01",
    #     "identifier": [{
    #         "type": {
    #             "coding": [{
    #                 "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
    #                 "code": "MR"
    #             }]
    #         },
    #         "system": "2.16.840.1.113883.3.1674",
    #         "value": "MRN here"
    #     }]
    # },
    #     "request": {
    #          "method": "POST",
    #          "url": "Patient"
    #      }
    # },
    # {"resource": {
    #     "resourceType": "Practitioner",
    #     "identifier": [{
    #         "use": "official",
    #         "system": "http://hl7.org/fhir/sid/us-npi",
    #         "value": "1558565424"
    #     }],
    #     "name": [{
    #         "family": "Wood",
    #         "given": ["Sharice"],
    #         "suffix": ["MD"]
    #     }]
    # },
    #     "request": {
    #         "method": "POST",
    #         "url": "Practitioner"
    #     }
    # },
    # {"resource": {
    #     "resourceType": "Encounter",
    #     "status": "planned",
    #     "subject": {
    #         "reference": "Patient/54"
    #     },
    #     "serviceProvider": {
    #         "reference": "Organization/33",
    #         "display": "CCM T1 CLINIC"
    #     },
    #     "class": [{
    #         "coding": [{
    #             "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
    #             "code": "AMB",
    #             "display": "Outpatient Encounter"
    #         }]
    #     }],
    #     "participant": [{
    #         "actor": {
    #             "reference": "Practitioner/1558565424"
    #         }
    #     }]
    # },
    #     "request": {
    #         "method": "POST",
    #         "url": "Encounter"
    #     }
    # },
    # {"resource": {
    #     "resourceType": "DocumentReference",
    #     "id": "GIRAdocRef",
    #     "status": "current",
    #     "description": "GIRA",
    #     "type": {
    #         "coding": [{
    #             "system": "http://loinc.org",
    #             "code": "11502-2",
    #             "display": "Laboratory report"
    #         },
    #             {"system": "http://testDocument.org",
    #              "code": "1000267",
    #              "display": "External Genetics Report"
    #              }]
    #     },
    #     "subject": {
    #         "reference": "Patient/54"
    #     },
    #     "content": [{
    #         "attachment": {
    #             "contentType": "application/pdf",
    #             "data": encoded_string,
    #             "title": "Genome Informed Risk Assessment"
    #         }
    #     }],
    #     "context": [{
    #         "reference": "Encounter/example"
    #     }]
    # },
    #     "request": {
    #         "method": "POST",
    #         "url": "DocumentReference"
    #     }
    # }]

bundle0.entry = entry_list
client.resource('Bundle', **json.loads(bundle0.json())).save()
