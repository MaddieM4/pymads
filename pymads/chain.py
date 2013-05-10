class Chain(object):
    ''' Represents a source for DNS results, including filters '''
    def __init__(self, sources=[], filters=[]):
        self.sources = sources
        self.filters = filters

    def get(self, request):
        ''' Returns a generator '''
        results = set()
        for source in self.sources:
            results.add( set(source.get(request)) ) 
        for filt in self.filters:
            results = filt.process(results)
        return results
