# -*- coding: utf-8 -*-

# -- Sheet --

# import required packages
# import fhirclient
from fhirclient import client
from fhirclient.models import bundle, documentreference, domainresource, encounter, organization, patient, practitioner, reference, resource, observation
import base64
import json
import requests
from urllib import request, parse
# import fhir

# define server settings and connect
# settings = {
#     'app_id': 'emerge_gira_app',
#     'api_base': 'http://localhost:8080/fhir'
# }

smart = client.FHIRClient(settings=settings)

# find PDF file of interest and convert to base64
#with open('/data/workspace_files/testBase64.pdf', "rb") as pdf_file:
    #encoded_string = base64.b64encode(pdf_file.read())
    #encoded_string = str(encoded_string)

import base64
with open("/Users/casjk8/Documents/testBase64.pdf", "rb") as pdf_file:
    encoded_string = base64.b64encode(pdf_file.read())
    decoded_string = encoded_string.decode("utf-8")

print(decoded_string)

# datafile=open('/Users/casjk8/Documents/testBase64.pdf', 'rb')
# pdfdatab=datafile.read()    #this is binary data
# datafile.close()
# import codecs
# b64PDF = codecs.encode(pdfdatab, 'base64')
# Sb64PDF=b64PDF.decode('utf-8')

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

pat_object = patient.Patient(pat_json)

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

org_hosp_object = organization.Organization(org_hosp_json)

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

prac_object = practitioner.Practitioner(prac_json)

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

enc_object = encounter.Encounter(enc_json)

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
            "data": Sb64PDF,
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

docref_object = documentreference.DocumentReference(docref_json)

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
message_object = bundle.Bundle(message_json)

print(message_json)

import requests
import json

url = "https://llmirthuat02:40010/fhir/"

payload = json.dumps({
  "resourceType": "Bundle",
  "identifier": {
    "system": "http://cincinnatichildrens.org/emerge/bundle_identifier",
    "value": "GIRAbundle"
  },
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Organization",
        "id": "1702",
        "identifier": [
          {
            "system": "urn:ietf:rfc:3986",
            "value": "urn:oid:2.16.840.1.113883.3.1674"
          }
        ],
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
    },
    {
      "resource": {
        "resourceType": "Organization",
        "id": "1662",
        "identifier": [
          {
            "system": "urn:oid:2.16.840.1.113883.3.1674",
            "value": "20001408"
          }
        ],
        "type": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                "code": "dept",
                "display": "Hospital Department"
              }
            ]
          }
        ],
        "name": "CCM T1 CLINIC",
        "partOf": {
          "reference": "Organization/1702"
        }
      }
    },
    {
      "resource": {
        "resourceType": "Patient",
        "id": "1703",
        "identifier": [
          {
            "type": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                  "code": "MR"
                }
              ]
            },
            "system": "urn:oid:2.16.840.1.113883.3.1674",
            "value": "mrn010101"
          }
        ],
        "name": [
          {
            "use": "official",
            "family": "last_name",
            "given": [
              "first_name"
            ]
          }
        ],
        "birthDate": "1974-12-25",
        "gender": "male"
      }
    },
    {
      "resource": {
        "resourceType": "Practitioner",
        "id": "1704",
        "identifier": [
          {
            "use": "official",
            "system": "http://hl7.org/fhir/sid/us-npi",
            "value": "1558565424"
          }
        ],
        "name": [
          {
            "family": "Wood",
            "given": [
              "Sharice"
            ],
            "suffix": [
              "MD"
            ]
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "Encounter",
        "id": "1705",
        "status": "planned",
        "subject": {
          "reference": "Patient/1703"
        },
        "serviceProvider": {
          "reference": "Organization/1662"
        },
        "class": {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
          "code": "AMB",
          "display": "ambulatory"
        },
        "participant": [
          {
            "individual": {
              "reference": "Practitioner/1704"
            }
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "DocumentReference",
        "id": "1706",
        "status": "current",
        "description": "GIRA",
        "type": {
          "coding": [
            {
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
          "reference": "Patient/1703"
        },
        "content": [
          {
            "attachment": {
              "contentType": "application/pdf",
              "data": "JVBERi0xLjMKJcTl8uXrp/Og0MTGCjMgMCBvYmoKPDwgL0ZpbHRlciAvRmxhdGVEZWNvZGUgL0xl\nbmd0aCAzMTkgPj4Kc3RyZWFtCngBnZIxT8MwEIX3/IoHbakN1LGdxPYxgli6VfJGmCIxIHWo8v8l\nzk6TUAVBhTLkcj6/e/flTjjghPKlN+h66Pz0Hae0svXwnQJj0QRSZNEd8Rz5VGtdIXbwTa7iVx20\nMjo41F4X8YgyRguD+AFxc7tab1YS8ROvMXf8XX4WdZVT3ld+KfoGsZbYcU+IzRjc5aCC2OagzjXG\npJp2rmrlRhbDzVZIGK0CxL3kqRYX3hH3f3guBiSzZyKntKts8owLEOz5YTT2OFrdpcZscJs9sQOV\nEnZ2VEoERWkCnU54umleM6nYUZfnIGULUeUEy0wo6pxpIKagOc886fE/Yi5c8o2WkwUlMFMrf74V\nUiefEV+BadicYsZkApEyPu/LJSZBV6zKAruhRitqwhK7ePqfniMVyPygx7zGVT58AT5AoJwKZW5k\nc3RyZWFtCmVuZG9iagoxIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL1Jlc291\ncmNlcyA0IDAgUiAvQ29udGVudHMgMyAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5k\nb2JqCjQgMCBvYmoKPDwgL1Byb2NTZXQgWyAvUERGIC9UZXh0IF0gL0NvbG9yU3BhY2UgPDwgL0Nz\nMSA1IDAgUiA+PiAvRm9udCA8PCAvVFQyIDcgMCBSCj4+ID4+CmVuZG9iago4IDAgb2JqCjw8IC9O\nIDMgL0FsdGVybmF0ZSAvRGV2aWNlUkdCIC9MZW5ndGggMjYxMiAvRmlsdGVyIC9GbGF0ZURlY29k\nZSA+PgpzdHJlYW0KeAGdlndUU9kWh8+9N73QEiIgJfQaegkg0jtIFQRRiUmAUAKGhCZ2RAVGFBEp\nVmRUwAFHhyJjRRQLg4Ji1wnyEFDGwVFEReXdjGsJ7601896a/cdZ39nnt9fZZ+9917oAUPyCBMJ0\nWAGANKFYFO7rwVwSE8vE9wIYEAEOWAHA4WZmBEf4RALU/L09mZmoSMaz9u4ugGS72yy/UCZz1v9/\nkSI3QyQGAApF1TY8fiYX5QKUU7PFGTL/BMr0lSkyhjEyFqEJoqwi48SvbPan5iu7yZiXJuShGlnO\n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\nj20gbUjZ8MtGy41lG99uit7UUaBRsL5gaLPv5sZCuUJR4b0tzlsObMVsFWzt3WazrWrblyJe0fVi\ny+KK4k8l3JLr31l9V/ndzPaE7b2l9qX7d+B2CHfc3em681iZYlle2dCu4F2t5czyovK3u1fsvlZh\nW3FgD2mPZI+0MqiyvUqvakfVp+qk6oEaj5rmvep7t+2d2sfb17/fbX/TAY0DxQc+HhQcvH/I91Br\nrUFtxWHc4azDz+ui6rq/Z39ff0TtSPGRz0eFR6XHwo911TvU1zeoN5Q2wo2SxrHjccdv/eD1Q3sT\nq+lQM6O5+AQ4ITnx4sf4H++eDDzZeYp9qukn/Z/2ttBailqh1tzWibakNml7THvf6YDTnR3OHS0/\nm/989Iz2mZqzymdLz5HOFZybOZ93fvJCxoXxi4kXhzpXdD66tOTSna6wrt7LgZevXvG5cqnbvfv8\nVZerZ645XTt9nX297Yb9jdYeu56WX+x+aem172296XCz/ZbjrY6+BX3n+l37L972un3ljv+dGwOL\nBvruLr57/17cPel93v3RB6kPXj/Mejj9aP1j7OOiJwpPKp6qP6391fjXZqm99Oyg12DPs4hnj4a4\nQy//lfmvT8MFz6nPK0a0RupHrUfPjPmM3Xqx9MXwy4yX0+OFvyn+tveV0auffnf7vWdiycTwa9Hr\nmT9K3qi+OfrW9m3nZOjk03dp76anit6rvj/2gf2h+2P0x5Hp7E/4T5WfjT93fAn88ngmbWbm3/eE\n8/sKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqClsgL0lDQ0Jhc2VkIDggMCBSIF0KZW5kb2JqCjIg\nMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9NZWRpYUJveCBbMCAwIDYxMiA3OTJdIC9Db3VudCAxIC9L\naWRzIFsgMSAwIFIgXSA+PgplbmRvYmoKOSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMg\nMiAwIFIgPj4KZW5kb2JqCjcgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1RydWVUeXBl\nIC9CYXNlRm9udCAvQUFBQUFDK0NhbGlicmkgL0ZvbnREZXNjcmlwdG9yCjEwIDAgUiAvVG9Vbmlj\nb2RlIDExIDAgUiAvRmlyc3RDaGFyIDMzIC9MYXN0Q2hhciA1OCAvV2lkdGhzIFsgNDg3IDUyNSAy\nMjkKMzkxIDIyNiAyMzkgNTI1IDMzNSA0NzkgNDk4IDUyNSA1MjcgNDIzIDc5OSA1MjUgMzI2IDYy\nMyA1MjUgMzA1IDIyOSA0NTMgNzE1CjM0OSA0NTUgNjkwIDI1MiBdID4+CmVuZG9iagoxMSAwIG9i\nago8PCAvTGVuZ3RoIDM3MCAvRmlsdGVyIC9GbGF0ZURlY29kZSA+PgpzdHJlYW0KeAFdkstugzAQ\nRfd8hZftIsI88pIQUpUqEos+1LQfAPYQIRWDDFnw973XSVOpi7M4eMaayzg+VM+V62YVv/vBnGRW\nbeesl2m4eCOqkXPnoiRVtjPzzcI309djFKP5tEyz9JVrB1UUkVLxB1qm2S/q4ckOjTzy25u34jt3\nVg9fh1P4crqM47f04malo7JUVlpc91KPr3UvKg6tq8rivJuXFbr+Kj6XURQmQkdyHckMVqaxNuJr\nd5ao0LosjscyEmf/HaX5taNpb6VpUhZE63VeRkWaQjPqZkfNoUDrbUZdQ4HWqaZuoADFNXULBShe\nU3dQAA0376EAxQlPayiAhuIGCqCh2EABtGWxhQJoGEOgbVCL0wxpCabizRnSEK1zRsiQiGAMzpwh\nHMFVGyrCEaihIhxB8Z6KcAS6pSIcgaZUhCPobagIR1KNfwJFOIKpJGzi95dzKXw892Wbi/fYc3hh\n4QlwtZ2T+yMch5GrDPwAoZ66FAplbmRzdHJlYW0KZW5kb2JqCjEwIDAgb2JqCjw8IC9UeXBlIC9G\nb250RGVzY3JpcHRvciAvRm9udE5hbWUgL0FBQUFBQytDYWxpYnJpIC9GbGFncyA0IC9Gb250QkJv\neCBbLTUwMyAtMzEzIDEyNDAgMTAyNl0KL0l0YWxpY0FuZ2xlIDAgL0FzY2VudCA5NTIgL0Rlc2Nl\nbnQgLTI2OSAvQ2FwSGVpZ2h0IDYzMiAvU3RlbVYgMCAvWEhlaWdodAo0NjQgL0F2Z1dpZHRoIDUy\nMSAvTWF4V2lkdGggMTMyOCAvRm9udEZpbGUyIDEyIDAgUiA+PgplbmRvYmoKMTIgMCBvYmoKPDwg\nL0xlbmd0aDEgMjMwNzIgL0xlbmd0aCAxMjAwOCAvRmlsdGVyIC9GbGF0ZURlY29kZSA+PgpzdHJl\nYW0KeAHVfHdcVFf+9rn3Ti9MYQYGBpiBoToUBURAhFGKFAuoo6CiNGuw1xgLUdNI3CSbaqqbTV1T\n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\n36ZS32w/okl26t0WepSCgufz8b3ge/QfDnYEGQGW40JWPPJ+clD1qIdZo7W0Iq+sNJdC+n0uVRMR\nJU4IW3dNXm7VfwC+3ZBwSvyXBhr8ioBMpq9Kf2V794qO9Sv+D0X1SMwKZW5kc3RyZWFtCmVuZG9i\nagoxMyAwIG9iago8PCAvVGl0bGUgKE1pY3Jvc29mdCBXb3JkIC0gRG9jdW1lbnQxKSAvUHJvZHVj\nZXIgKG1hY09TIFZlcnNpb24gMTMuMi4xIFwoQnVpbGQgMjJENjhcKSBRdWFydHogUERGQ29udGV4\ndCkKL0NyZWF0b3IgKFdvcmQpIC9DcmVhdGlvbkRhdGUgKEQ6MjAyMzA2MjgwMDU2NTZaMDAnMDAn\nKSAvTW9kRGF0ZSAoRDoyMDIzMDYyODAwNTY1NlowMCcwMCcpCj4+CmVuZG9iagp4cmVmCjAgMTQK\nMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwNDEzIDAwMDAwIG4gCjAwMDAwMDMzNjEgMDAwMDAg\nbiAKMDAwMDAwMDAyMiAwMDAwMCBuIAowMDAwMDAwNTE3IDAwMDAwIG4gCjAwMDAwMDMzMjYgMDAw\nMDAgbiAKMDAwMDAwMDAwMCAwMDAwMCBuIAowMDAwMDAzNDkzIDAwMDAwIG4gCjAwMDAwMDA2MTQg\nMDAwMDAgbiAKMDAwMDAwMzQ0NCAwMDAwMCBuIAowMDAwMDA0MTk4IDAwMDAwIG4gCjAwMDAwMDM3\nNTUgMDAwMDAgbiAKMDAwMDAwNDQzNCAwMDAwMCBuIAowMDAwMDE2NTMyIDAwMDAwIG4gCnRyYWls\nZXIKPDwgL1NpemUgMTQgL1Jvb3QgOSAwIFIgL0luZm8gMTMgMCBSIC9JRCBbIDwwY2UxZDk2ODlh\nNzBhNTA4OTlkNTY1NjAzYzc1NDg4MT4KPDBjZTFkOTY4OWE3MGE1MDg5OWQ1NjU2MDNjNzU0ODgx\nPiBdID4+CnN0YXJ0eHJlZgoxNjc0OAolJUVPRgo=\n",
              "title": "Genome Informed Risk Assessment"
            }
          }
        ],
        "context": {
          "encounter": [
            {
              "reference": "Encounter/1705"
            }
          ]
        }
      }
    }
  ]
})
headers = {
  'Content-Type': 'application/json'
 # 'Authorization': 'Basic ZU1lcmdlOmVNZXJnZQ=='
}

# response = requests.request("POST", url, headers=headers, data=payload, verify='/Users/casjk8/Documents/llmirthuat02.pem')

r = requests.post('https://llmirthuat02:40010/fhir/', data=payload, auth=(USER, PASS), headers=headers, verify='/Users/casjk8/Documents/llmirthuat02.pem')
print(r.text)

#print(response.text)

# test pull for GIRA
# docs = documentreference.DocumentReference.read("1706", smart.server)

