#Imports
from fhirpy import SyncFHIRClient
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.documentreference import *
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.bundle import Bundle

import json
# settings = {
#     'app_id': 'my_web_app',
#     'api_base': 'http://localhost:8080/fhir'
# }
#
# smart = client.FHIRClient(settings=settings)
# import fhirclient.models.patient as p
# patient = p.Patient.read()

client = SyncFHIRClient(url='http://localhost:8080/fhir')

patients_resources = client.resources('Patient')
doc_resources = client.resources('DocumentReference')
bundle_resources = client.resources('Bundle')
type = { CodeableConcept }
content = [
    {
        "attachment": {
            "url": "file:///Users/casjk8/Documents/JC_Mar10_Mike.pdf",
            "title": "SamplePDF"
        }
    }
]
doc0 = DocumentReference(status="current", content=content)
client.resource('DocumentReference',**json.loads(doc0.json())).save()

# try to make bundle
bundle0 = Bundle(type="transaction")

entrylist = [{
            "resource": {
                "resourceType": "Patient",
                "id": "2",
                "birthDate": "2008-01-06",
                "identifier": [
                    {
                        "value": "mrn22222",
                        "system": "http://example.org/fhir/mrn"
                    }
                ]
            },
            "request": {
                "method": "POST",
                "url": "Patient"
            }
    },
        {
            "resource": {
                "resourceType": "DocumentReference",
                "id": "GirsDocumentReferenceExample",
                "status": "current",
                "description": "Test Description",
                "type": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "11502-2"
                    }],
                    "text": "Laboratory report"
                },
                "subject": {
                    "reference": "Patient/2",
                    "identifier": {
                        "system": "http://example.org/fhir/mrn",
                        "value": "mrn22222"
                    }
                },
                "content": [{
                    "attachment": {
                        "url": "file:///Users/casjk8/Documents/JC_Mar10_Mike.pdf",
                        "title": "SamplePDF"
                    }
                }]
            },
            "request": {
                "method": "POST",
                "url": "DocumentReference"
            },
            {
            "resource": {
                "resourceType": "Appointment",
                "id": "",
                "identifier": [
                    {
                        "value": "mrn22222",
                        "system": "http://example.org/fhir/mrn"
                    }
                ],
                "status": "",
                "serviceCategory": ""
            },
            "request": {
                "method": "POST",
                "url": "Patient"
            }
    },
        }
        ]


bundle0.entry = entrylist
client.resource('Bundle',**json.loads(bundle0.json())).save()

#Part 2----------------------------------------------------------------------------------------------------------------------------------------------------
#We want to create a patient and save it into our server

#Create a new patient using fhir.resources
patient0 = Patient()

#Create a HumanName and fill it with the information of our patient
name = HumanName()
name.use = "official"
name.family = "familyname"
name.given = ["givenname1","givenname2"]

patient0.name = [name]

#Check our patient in the terminal
print()
print("Our patient : ",patient0)
print()

#Save (post) our patient0, it will create it in our server
client.resource('Patient',**json.loads(patient0.json())).save()

#Part 3----------------------------------------------------------------------------------------------------------------------------------------------------
#Now we want to get a certain patient and add his phone number and change his name before saving our changes in the server

#Get the patient as a fhir.resources Patient of our list of patient resources who has the right name, for convenience we will use the patient we created before
patient0 = Patient.parse_obj(patients_resources.search(family='familyname',given='givenname1').first().serialize())

#Create our patient new phone number
telecom = ContactPoint()
telecom.value = '555-748-7856'
telecom.system = 'phone'
telecom.use = 'home'

#Add our patient phone to it's dossier
patient0.telecom = [telecom]

#Change the second given name of our patient to "anothergivenname"
patient0.name[0].given[1] = "anothergivenname"

#Check our Patient in the terminal
print()
print("Our patient with the phone number and the new given name : ",patient0)
print()

#Save (put) our patient0, this will save the phone number and the new given name to the existing patient of our server
client.resource('Patient',**json.loads(patient0.json())).save()

#Part 4----------------------------------------------------------------------------------------------------------------------------------------------------
#Now we want to create an observation for our client

#Get the id of the patient you want to attach the observation to
id = Patient.parse_obj(patients_resources.search(family='familyname',given='givenname1').first().serialize()).id
print("id of our patient : ",id)

#Set our code in our observation, code which hold codings which are composed of system, code and display
coding = Coding()
coding.system = "https://loinc.org"
coding.code = "1920-8"
coding.display = "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma"
code = CodeableConcept()
code.coding = [coding]
code.text = "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma"

#Create a new observation using fhir.resources, we enter status and code inside the constructor since theuy are necessary to validate an observation
observation0 = Observation(status="final",code=code)

#Set our category in our observation, category which hold codings which are composed of system, code and display
coding = Coding()
coding.system = "https://terminology.hl7.org/CodeSystem/observation-category"
coding.code = "laboratory"
coding.display = "laboratory"
category = CodeableConcept()
category.coding = [coding]
observation0.category = [category]

#Set our effective date time in our observation
observation0.effectiveDateTime = "2012-05-10T11:59:49+00:00"

#Set our issued date time in our observation
observation0.issued = "2012-05-10T11:59:49.565+00:00"

#Set our valueQuantity in our observation, valueQuantity which is made of a code, a unir, a system and a value
valueQuantity = Quantity()
valueQuantity.code = "U/L"
valueQuantity.unit = "U/L"
valueQuantity.system = "https://unitsofmeasure.org"
valueQuantity.value = 37.395
observation0.valueQuantity = valueQuantity

#Setting the reference to our patient using his id
reference = Reference()
reference.reference = f"Patient/{id}"
observation0.subject = reference

#Check our observation in the terminal
print()
print("Our observation : ",observation0)
print()

#Save (post) our observation0 using our client
client.resource('Observation',**json.loads(observation0.json())).save()

test_json = {
    "resourceType": "Bundle",
    "identifier": "GIRAbundle",
    "type": "transaction",
    "timestamp": "2023-06-04T20:33:22.422Z",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "1",
                "birthDate": "2008-01-06",
                "identifier": [
                    {
                        "value": "0000000001",
                        "type": {
                            "text": "MR"
                        }
                    }
                ]
            }
        }
        ],
    "entry": [
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
                    }
                ]
            },}
    ]
}
bundle0 = Bundle(type="message")
doc_entry = {
            "resource": {
                "resourceType": "DocumentReference",
                "id": "GirsDocumentReferenceExample",
                "subject": {
                    "reference": "Patient/GIRApatient"
                },
                "status": "current",
                "description": "Test Description",
                "type": {
                    "text": "Laboratory report"
                },
                "content": [
                    {
                        "attachment": {
                            "url": "file:///Users/casjk8/Documents/JC_Mar10_Mike.pdf",
                            "title": "SamplePDF"
                        }
                    }
                ]
            },
    "request": {
        "method": "POST",
        "url": "DocumentReference"
    }
}
pat_entry =         {
            "resource": {
                "resourceType": "Patient",
                "id": "1",
                "birthDate": "2008-01-06",
                "identifier": [
                    {
                        "value": "0000000001",
                        "type": {
                            "text": "MR"
                        }
                    }
                ]
            },
    "request": {
        "method": "POST",
        "url": "Patient",
        "ifNoneExist": "identifier=http://acme.org/mrns|12345"
    }
}
header_entry = {
            "resource": {
                "resourceType": "MessageHeader",
                "id": "GIRAMessageHeaderExample",
                "eventCoding": {
                    "system": "HTTP://EXAMPLE.ORG/FHIR/MESSAGE-EVENTS",
                    "code": "ADMIN-NOTIFY"
                },
                "source": {
                    "name": "ACME CENTRAL PATIENT REGISTRY"
                }
            },
    "request": {
      "method": "POST",
      "url": "MessageHeader"
        }
}
entry = [
        {
            {
            "resource": {
                "resourceType": "MessageHeader",
                "id": "GIRAMessageHeaderExample",
            }
        },
        {
            "resource": {
                "resourceType": "Patient",
                "id": "1",
                "birthDate": "2008-01-06",
                "identifier": [
                    {
                        "value": "0000000001",
                        "type": {
                            "text": "MR"
                        }
                    }
                ]
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
                    }
                    ]
                }
            }
        }
    ]



entry = header_entry, pat_entry, doc_entry
client.resource('Bundle',**json.loads(bundle0.json())).save()
