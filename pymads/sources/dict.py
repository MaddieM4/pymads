class DictSource(object):
    '''
    Simplest source. All data in memory, in the form of a dict.

    Data format:
        {
            'mydomain.com' : [
                <pymads.record.Record>
            ],
            'myotherdomain.com' : [
                <pymads.record.Record>,
                <pymads.record.Record>,
            ]
        }
    '''
    def __init__(self, data = {}):
        self.data = {}
        self.data.update(data)

    def get(self, domain):
        result = set()
        if domain in self.data:
            result.update(set(self.data[domain]))
        return result
