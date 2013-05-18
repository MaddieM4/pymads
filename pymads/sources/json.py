from __future__ import absolute_import

import json

from pymads.record import Record
from pymads.sources.dict import DictSource

class JSONSource(DictSource):
    '''
    Subclass of DictSource, pulls data from JSON file.

    Data format:
        {
            "mydomain.com" : [
                {
                    "rdata": "6.6.6.6"
                }
            ],
            "myotherdomain.com" : [
                {
                    "rdata": "9.9.9.9"
                },
                {
                    "type" : "AAAA",
                    "rdata": "fcd9:e703:498e:5d07:e5fc:d525:80a6:a51c"
                }
            ]
        }
    '''
    def __init__(self, path):
        data = json.load(open(path))
        for k in data:
            records = data[k]
            if type(records) != list:
                raise TypeError("JSONSource expects each top-level value to be a list of records")

            data[k] = [toRecord(r, k) for r in records]
        DictSource.__init__(self, data)

def toRecord(record, fallback_domain):
    if type(record) != dict:
        raise TypeError("JSONSource expects each top-level value to be a list of record dicts")
    if not 'domain_name' in record:
        record['domain_name'] = fallback_domain
    return Record(**record)
