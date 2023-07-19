#Imports
from fhirpy import SyncFHIRClient
from fhir.resources.bundle import Bundle

import json
import base64

# personal test HAPI FHIR server
client = SyncFHIRClient(url='http://localhost:8080/fhir')

# endpoint from Sai
client = SyncFHIRClient(url='https://llmirthuat02:40010/fhir/')

# find PDF file of interest and convert to base64
with open("/Users/casjk8/Documents/testBase64.pdf", "rb") as pdf_file:
    encoded_string = base64.b64encode(pdf_file.read())

# entire raw message
whole_message = {
    "resourceType": "Bundle",
    "identifier": "GIRAbundle",
    "type": "transaction",
    "entry":
        [
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": "33",
                    "identifier": [{
                        "system": "http://testOrganization.org",
                        "value": "20001408"
                    }],
                },
                "request": {
                    "method": "POST",
                    "url": "Organization"
                }
            },
            {"resource": {
                "resourceType": "Patient",
                "id": "54",
                "birthDate": "2010-01-01",
                "identifier": [{
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR"
                        }]
                    },
                    "system": "",
                    "value": "mrn010101"
                }]
            },
                "request": {
                    "method": "POST",
                    "url": "Patient"
                }
            },
            {"resource": {
                "resourceType": "Practitioner",
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
            },
                "request": {
                    "method": "POST",
                    "url": "Practitioner"
                }
            },
            {"resource": {
                "resourceType": "Encounter",
                "status": "planned",
                "subject": {
                    "reference": "Patient/54"
                },
                "serviceProvider": {
                    "reference": "Organization/33",
                    "display": "CCM T1 CLINIC"
                },
                "class": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                        "display": "Outpatient Encounter"
                    }]
                }],
                "participant": [{
                    "actor": {
                        "reference": "Practitioner/1558565424"
                    }
                }]
            },
                "request": {
                    "method": "POST",
                    "url": "Encounter"
                }
            },
            {"resource": {
                "resourceType": "DocumentReference",
                "id": "GIRAdocRef",
                "status": "current",
                "description": "GIRA",
                "type": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "11502-2",
                        "display": "Laboratory report"
                    },
                        {"system": "http://testDocument.org",
                         "code": "1000267",
                         "display": "External Genetics Report"
                         }]
                },
                "subject": {
                    "reference": "Patient/54"
                },
                "content": [{
                    "attachment": {
                        "contentType": "application/pdf",
                        "data": encoded_string,
                        "title": "Genome Informed Risk Assessment"
                    }
                }],
                "context": [{
                    "reference": "Encounter/example"
                }]
            },
                "request": {
                    "method": "POST",
                    "url": "DocumentReference"
                }
            }]
}

# fhirpy version
bundle0 = Bundle(type="transaction")

entrylist = [
    {
        "resource": {
            "resourceType": "Organization",
            "id": "33",
            "identifier": [{
                "system": "http://testOrganization.org",
                "value": "20001408"
            }],
        },
        "request": {
            "method": "POST",
            "url": "Organization"
        }
    },
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
    {"resource": {
        "resourceType": "Patient",
        "birthDate": "2010-01-01",
        "identifier": [{
            "type": {
                "coding": [{
                    "system": "",
                    "code": "MR"
                }]
            },
            "system": "",
            "value": "MRN here"
        }]
    },
    }
    {"resource": {
        "resourceType": "Practitioner",
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
    },
        "request": {
            "method": "POST",
            "url": "Practitioner"
        }
    },
    {"resource": {
        "resourceType": "Encounter",
        "status": "planned",
        "subject": {
            "reference": "Patient/54"
        },
        "serviceProvider": {
            "reference": "Organization/33",
            "display": "CCM T1 CLINIC"
        },
        "class": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "Outpatient Encounter"
            }]
        }],
        "participant": [{
            "actor": {
                "reference": "Practitioner/1558565424"
            }
        }]
    },
        "request": {
            "method": "POST",
            "url": "Encounter"
        }
    },
    {"resource": {
        "resourceType": "DocumentReference",
        "id": "GIRAdocRef",
        "status": "current",
        "description": "GIRA",
        "type": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "11502-2",
                "display": "Laboratory report"
            },
                {"system": "http://testDocument.org",
                 "code": "1000267",
                 "display": "External Genetics Report"
                 }]
        },
        "subject": {
            "reference": "Patient/54"
        },
        "content": [{
            "attachment": {
                "contentType": "application/pdf",
                "data": encoded_string,
                "title": "Genome Informed Risk Assessment"
            }
        }],
        "context": [{
            "reference": "Encounter/example"
        }]
    },
        "request": {
            "method": "POST",
            "url": "DocumentReference"
        }
    }]

bundle0.entry = entrylist
client.resource('Bundle',**json.loads(bundle0.json())).save()
