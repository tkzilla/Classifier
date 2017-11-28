"""
VISA: .tiq File Trace Grabber
Author: Morgan Allison
Date edited: 9/17
Loads a bunch of .tiq files containing the same kind of waveform,
processes and transfers multiple spectrums per acquisition,
and saves a .csv file when finished.
Windows 7 64-bit
Python 3.6.1 64-bit (Anaconda 4.4.0)
NumPy 1.11.2, PyVISA 1.8, PyVISA-py 0.2
Download Anaconda: http://continuum.io/downloads
Anaconda includes NumPy
"""

import visa
from time import sleep
import numpy as np
from os import listdir
import matplotlib.pyplot as plt
import pandas as pd

rm = visa.ResourceManager()

def get_file_list(path):
    if isinstance(path, str):
        if path[-1] != '\\':
            raise FileNotFoundError('\'path\' must end in \'\\\\\'')
        return [path + f for f in listdir(path)]
    else:
        raise TypeError('\'path\' must be a string')


def get_filename_from_path(filePath):
     if not isinstance(filePath, str):
         raise TypeError('\'filePath\' must be a string')
     else:
         return filePath.split('\\')[-1]
    

"""#################RSA SETUP#################"""
# rsa = rm.open_resource('GPIB8::1::INSTR')
rsa = rm.open_resource('TCPIP::127.0.0.1::INSTR')
rsa.timeout = 5000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print(rsa.query('*idn?'))
# rsa.write('*rst')
rsa.write('*cls')

# fileName = 'C:\\signalvu-pc files\\classifier\\n\\802.11n_20MHz_2.412GHzcf_master_1.tiq'

cf = 2.412e9
traceLength = 801
rsa.write('display:general:measview:new toverview')

rsa.write('spectrum:frequency:center {}'.format(cf))

analysisLength = 40e-6
spectrumLength = 7e-6
# rsa.write('sense:spectrum:points:count {}'.format(traceLength))
# rsa.write('sense:spectrum:time:mode independent')
# rsa.write('sense:analysis:length {}'.format(analysisLength))
# rsa.write('sense:spectrum:length {}'.format(spectrumLength))

offset = [o*1e-6 for o in range(25)]
inner = len(offset)

path = 'C:\\signalvu-pc files\\classifier dataset\\n\\adds\\'
fList = get_file_list(path)
# 1 = 802.11n, 2 = 802.11b, 3 = bluetooth
label = 1

for f in fList:
    print('Loading ', get_filename_from_path(f))
    rsa.write('mmemory:load:iq "{}"'.format(f))
    rsa.query('*opc?')
    
    length = int(rsa.query('sense:reanalyze:select:acquisition:last?'))
    outer = length
    print(length, 'acquisitions in file')
    
    rsa.write('sense:reanalyze:first')
    rsa.query('*opc?')
    traces = []
    rsa.timeout = 30000
    for i in range(outer):
        # print('Acquisition ', rsa.query('sense:reanalyze:current:acquisition?'))
        for o in offset:
            rsa.write('sense:spectrum:start {}'.format(o))
            rsa.write('sense:reanalyze:current')
            rsa.query('*opc?')
            temp = rsa.query_binary_values('fetch:spectrum:trace1?',
                                           datatype='f')
            # this is the label
            temp.append(label)
            
            traces.append(temp)
        rsa.write('sense:reanalyze:next')
        rsa.query('*opc?')
        # print(np.shape(traces))
        
outFileName = 'adds.csv'
print(np.shape(traces))
np.savetxt(outFileName, traces, delimiter=',')

try:
    rsa.close()
except:
    pass
