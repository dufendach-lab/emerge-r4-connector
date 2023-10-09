#Imports
# from fhirpy import SyncFHIRClient
# from fhir.resources.bundle import Bundle
# from fhir.resources.encounter import Encounter
from fhirclient import client, auth
from fhirclient.models import patient, organization, encounter, bundle, resource, domainresource, reference, practitioner, documentreference
import json
import base64

# personal test HAPI FHIR server
#client = SyncFHIRClient(url='http://localhost:8080/fhir')

# endpoint from Sai
# client = SyncFHIRClient(url='https://llmirthuat02:40010/fhir/')
settings = {
  'app_id': 'emerge_gira_app',
  'api_base': 'http://localhost:8080/fhir'
}
smart = client.FHIRClient(settings=settings)
auth0 =
smart.authorize()
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
    "class": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB",
        "display": "ambulatory"
    },
    "participant": [{
            "individual": {
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
    "context": {
        "encounter": [
            {
                "reference": to_reference(enc_const)
            }
        ]
    }
}

# entire raw message
message_const = {
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
}


# bundle.Bundle.
#     entry_list = [
#     {"resource": org_hosp_const,
#      "request": {
#          "method": "POST",
#          "url": "Organization"
#      }
#      },
#     {"resource": org_dept_const,
#      "request": {
#          "method": "POST",
#          "url": "Organization"
#      }
#      },
#     {"resource": pat_const,
#      "request": {
#          "method": "POST",
#          "url": "Patient"
#      }
#      },
#     {"resource": enc_const,
#      "request": {
#          "method": "POST",
#          "url": "Encounter"
#      }
#      },
#     {"resource": docref_const,
#      "request": {
#          "method": "POST",
#          "url": "DocumentReference"
#      }
#      }
# ])

# fhirpy version

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

# bundle0.entry = entry_list
# client.resource('Bundle', **json.loads(bundle0.json())).save()

##################
fhirclient.client.FHIRClient.
smart.authorize()
bundle0 = bundle.Bundle(jsondict=message_const, )
('Bundle',**json.loads(bundle0.json())).save()
smart.save_state(bundle'**json.loads(bundle0.json()))
bundle0.create(server=smart.server)

as_json
# {
#   "entry": [
#     {
#       "fullUrl": "urn:uuid:61ebe359-bfdc-4613-8bf2-c5e300945f0a",
#       "resource": {
#         "resourceType": "Patient",
#         "text": {
#           "status": "generated",
#           "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Some narrative</div>"
#         },
#         "active": true,
#         "name": [
#           {
#             "use": "official",
#             "family": "Chalmers",
#             "given": [
#               "Peter",
#               "James"
#             ]
#           }
#         ],
#         "gender": "male",
#         "birthDate": "1974-12-25"
#       },
#       "request": {
#         "method": "POST",
#         "url": "Patient"
#       }
#     },
#     {
#       "fullUrl": "urn:uuid:88f151c0-a954-468a-88bd-5ae15c08e059",
#       "resource": {
#         "resourceType": "Patient",
#         "text": {
#           "status": "generated",
#           "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Some narrative</div>"
#         },
#         "identifier": [
#           {
#             "system": "http:/example.org/fhir/ids",
#             "value": "234234"
#           }
#         ],
#         "active": true,
#         "name": [
#           {
#             "use": "official",
#             "family": "Chalmers",
#             "given": [
#               "Peter",
#               "James"
#             ]
#           }
#         ],
#         "gender": "male",
#         "birthDate": "1974-12-25"
#       },
#       "request": {
#         "method": "POST",
#         "url": "Patient",
#         "ifNoneExist": "identifier=http:/example.org/fhir/ids|234234"
#       }
#     },
#     {
#       "fullUrl": "http://example.org/fhir/Patient/123",
#       "resource": {
#         "resourceType": "Patient",
#         "id": "123",
#         "text": {
#           "status": "generated",
#           "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Some narrative</div>"
#         },
#         "active": true,
#         "name": [
#           {
#             "use": "official",
#             "family": "Chalmers",
#             "given": [
#               "Peter",
#               "James"
#             ]
#           }
#         ],
#         "gender": "male",
#         "birthDate": "1974-12-25"
#       },
#       "request": {
#         "method": "PUT",
#         "url": "Patient/123"
#       }
#     },
#     {
#       "fullUrl": "urn:uuid:74891afc-ed52-42a2-bcd7-f13d9b60f096",
#       "resource": {
#         "resourceType": "Patient",
#         "text": {
#           "status": "generated",
#           "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Some narrative</div>"
#         },
#         "identifier": [
#           {
#             "system": "http:/example.org/fhir/ids",
#             "value": "456456"
#           }
#         ],
#         "active": true,
#         "name": [
#           {
#             "use": "official",
#             "family": "Chalmers",
#             "given": [
#               "Peter",
#               "James"
#             ]
#           }
#         ],
#         "gender": "male",
#         "birthDate": "1974-12-25"
#       },
#       "request": {
#         "method": "PUT",
#         "url": "Patient?identifier=http:/example.org/fhir/ids|456456"
#       }
#     },
#     {
#       "fullUrl": "http://example.org/fhir/Patient/123a",
#       "resource": {
#         "resourceType": "Patient",
#         "id": "123a",
#         "text": {
#           "status": "generated",
#           "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Some narrative</div>"
#         },
#         "active": true,
#         "name": [
#           {
#             "use": "official",
#             "family": "Chalmers",
#             "given": [
#               "Peter",
#               "James"
#             ]
#           }
#         ],
#         "gender": "male",
#         "birthDate": "1974-12-25"
#       },
#       "request": {
#         "method": "PUT",
#         "url": "Patient/123a",
#         "ifMatch": "W/\"2\""
#       }
#     },
#     {
#       "request": {
#         "method": "DELETE",
#         "url": "Patient/234"
#       }
#     },
#     {
#       "request": {
#         "method": "DELETE",
#         "url": "Patient?identifier=123456"
#       }
#     },
#     {
#       "fullUrl": "urn:uuid:79378cb8-8f58-48e8-a5e8-60ac2755b674",
#       "resource": {
#         "resourceType": "Parameters",
#         "parameter": [
#           {
#             "name": "coding",
#             "valueCoding": {
#               "system": "http://loinc.org",
#               "code": "1963-8"
#             }
#           }
#         ]
#       },
#       "request": {
#         "method": "POST",
#         "url": "ValueSet/$lookup"
#       }
#     },
#     {
#       "request": {
#         "method": "GET",
#         "url": "Patient?name=peter"
#       }
#     },
#     {
#       "request": {
#         "method": "GET",
#         "url": "Patient/12334",
#         "ifNoneMatch": "W/\"4\"",
#         "ifModifiedSince": "2015-08-31T08:14:33+10:00"
#       }
#     }
#   ]
# }