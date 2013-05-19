import subprocess

def dig(hostname, test_host='localhost', test_port=53000):
    sp = subprocess.Popen(
        ['dig', '@' + test_host, '-p%d' % test_port, hostname, 'ANY'],
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        universal_newlines = True
    )
    return sp.communicate()[0] # STDOUT
