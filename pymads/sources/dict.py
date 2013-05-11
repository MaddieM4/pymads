class DictSource(object):
    '''
    Simplest source. All data in memory, in the form of a dict.

    Data format:
        {
            'mydomain.com' : [
                ('A',  '7.7.7.7'),
                ('NS', '7.7.7.8'),
            ],
            'myotherdomain.com' : [
                ('A',    '8.9.8.9'),
                ('AAAA', 'fc99:76ad::0011'),
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
