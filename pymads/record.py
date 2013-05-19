import struct
from pymads import utils

class Record(object):
    ''' Represents a DNS record. '''

    def __init__(self, domain_name, rdata, 
                    rtype="A", rttl=1800, rclass="IN"):
        '''
            domain_name : A straightforward FQDN or PQDN
            rdata       : For most records, just IP string.
            rtype       : Record type. Usually A or AAAA.
            rttl        : Time-to-live (expiration data).
            rclass      : Almost always IN for Internet.
        '''
        self.domain_name = domain_name
        self.rdata  = rdata
        self.rtype  = rtype
        self.rttl   = int(rttl)
        self.rclass = rclass
        self.rdata_formatted = self.format_rdata()

    @property
    def rtypecode(self):
        return RECORD_TYPES[self.rtype]

    @property
    def rclasscode(self):
        return RECORD_CLASSES[self.rclass]

    def __hash__(self):
        return hash((
            self.domain_name,
            self.rdata,
            self.rtype,
            self.rttl,
            self.rclass,
        ))

    def format_rdata(self):
        '''
        Create the binary representation of the rdata for use in responses.
        '''
        # TODO : Support more special output types
        if self.rtype == 'A':
            segments = [int(x) for x in self.rdata.split('.')]
            if bytes == str:
                return bytes().join(chr(x) for x in segments)
            else:
                return bytes(segments)
        else:
            return byteify(self.rdata)

    def export(self):
        '''
        Formats the resource fields to be used in the response packet.
        '''

        r  = utils.labels2str(byteify(x) for x in self.domain_name.split('.'))
        r += struct.pack(
            "!HHIH",
             self.rtypecode,
             self.rclasscode,
             self.rttl,
             len(self.rdata_formatted)
        )
        r += self.rdata_formatted
        return r

def byteify(obj):
    try:
        return bytes(obj, 'utf-8')
    except:
        return str(obj)

# http://edgedirector.com/app/type.htm

RECORD_TYPES = {
    'A'        : 0x0001,
    'NS'       : 0x0002,
    'MD'       : 0x0003,
    'MF'       : 0x0004,
    'CNAME'    : 0x0005,
    'SOA'      : 0x0006,
    'MB'       : 0x0007,
    'MG'       : 0x0008,
    'MR'       : 0x0009,
    'NULL'     : 0x000a,
    'WKS'      : 0x000b,
    'PTR'      : 0x000c,
    'HINFO'    : 0x000d,
    'MINFO'    : 0x000e,
    'MX'       : 0x000f,

    'TXT'      : 0x0010,
    'RP'       : 0x0011,
    'AFSDB'    : 0x0012,
    'X25'      : 0x0013,
    'ISDN'     : 0x0014,
    'RT'       : 0x0015,
    'NSAP'     : 0x0016,
    'NSAPPTR'  : 0x0017,
    'SIG'      : 0x0018,
    'KEY'      : 0x0019,
    'PX'       : 0x001a,
    'GPOS'     : 0x001b,
    'AAAA'     : 0x001c,
    'LOC'      : 0x001d,
    'NXT'      : 0x001e,
    'EID'      : 0x001f,

    'NIMLOC'   : 0x0020,
    'SRV'      : 0x0021,
    'ATMA'     : 0x0022,
    'NAPTR'    : 0x0023,
    'KX'       : 0x0024,
    'CERT'     : 0x0025,
    'A6'       : 0x0026,
    'DNAME'    : 0x0027,
    'SINK'     : 0x0028,
    'OPT'      : 0x0029,
    'DS'       : 0x002B,
    'RRSIG'    : 0x002E,
    'NSEC'     : 0x002F,

    'DNSKEY'   : 0x0030,
    'DHCID'    : 0x0031,

    'UINFO'    : 0x0064,
    'UID'      : 0x0065,
    'GID'      : 0x0066,
    'UNSPEC'   : 0x0067,

    'ADDRS'    : 0x00f8,
    'TKEY'     : 0x00f9,
    'TSIG'     : 0x00fa,
    'IXFR'     : 0x00fb,
    'AXFR'     : 0x00fc,
    'MAILB'    : 0x00fd,
    'MAILA'    : 0x00fe,
    'ANY'      : 0x00ff,

    'WINS'     : 0xff01,
    'WINSR'    : 0xff02,
}

RECORD_CLASSES = {
    'IN'       : 0x0001, # Alias
    'INTERNET' : 0x0001,
    'CSNET'    : 0x0002,
    'CHAOS'    : 0x0003,
    'HESIOD'   : 0x0004,
    'NONE'     : 0x00fe,
    'ALL'      : 0x00ff,
    'ANY'      : 0x00ff,
}
