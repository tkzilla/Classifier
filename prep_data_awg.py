"""
VISA: SourceXpress/AWG Sequence Builder and Channel Skew Adjuster
Author: Morgan Allison
Date created: 5/17
Date edited: 5/17
Creates a sequence of two waveforms with an external trigger dependency
and configures the AWG to change its phase between waveform outputs
Windows 7 64-bit
Python 3.6.0 64-bit (Anaconda 4.3.0)
NumPy 1.11.2, PyVISA 1.8, PyVISA-py 0.2
Download Anaconda: http://continuum.io/downloads
Anaconda includes NumPy
"""

import visa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

rm = visa.ResourceManager()

# Change this to connect to your AWG as needed
"""#################SEARCH/CONNECT#################"""
# awg = rm.open_resource('TCPIP::192.168.1.8::INSTR')
awg = rm.open_resource('GPIB8::1::INSTR')
awg.timeout = 1000
awg.encoding = 'latin_1'
awg.write_termination = None
awg.read_termination = '\n'
print(awg.query('*idn?'))
awg.write('*cls')
#
#
# """#################AWG SETUP#################"""
# awg.write('*rst')
# setupFile = 'C:\\Users\\OEM\\Desktop\\Waveform Files\\misc\\classifier_clean.awgx'
# awg.write('mmemory:open:setup "{}"'.format(setupFile))
# print('sent mmemory command')
# awg.query('*opc?')
# print('done bitch')
trigInterval = 4

awg.write('trigger:interval {}'.format(trigInterval))

numSeq = awg.query('slist:size?')
# print(numSeq)
seqName = awg.query('slist:name? {}'.format(numSeq))
# print(seqName)
length = int(awg.query('slist:sequence:length? {}'.format(seqName)))

# # print(length, type(length))
# for step in range(length):
# #     awg.write('slist:seq:step{}:tflag1:aflag {}, pulse'.format(step+1,
# #                                                                seqName))
#     awg.write('slist:seq:step{}:winp {}, itrigger'.format(step+1, seqName))
# #     awg.write('slist:seq:step{}:ejin {}, off'.format(step+1, seqName))
#     awg.write('slist:seq:step{}:goto {}, next'.format(step+1, seqName))
#     if step < length:
#         awg.write('slist:seq:step{}:ejum {}, next'.format(step+1, seqName))
#     else:
#         awg.write('slist:seq:step{}:ejum {}, first'.format(step + 1, seqName))

# sampleRate = 24.12e9
# awg.write('clock:srate {}'.format(sampleRate))
# awg.write('source1:casset:sequence "{}", 1'.format(seqName))
# awg.write('source2:casset:sequence "{}", 2'.format(seqName))
# awg.write('output1:state on')
# awg.write('output2:state on')
# awg.write('awgcontrol:run:immediate')
# awg.query('*opc?')

# awg.write('output1 on')
# awg.write('awgcontrol:run:immediate')
# awg.query('*OPC?')

print(awg.query('system:error:all?'))


"""#################RSA SETUP#################"""
# rsa = rm.open_resource('GPIB8::1::INSTR')
rsa = rm.open_resource('TCPIP::192.168.1.19::INSTR')
rsa.timeout = 5000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print(rsa.query('*idn?'))
# rsa.write('*rst')
rsa.write('*cls')

trigLevel = -10
cf = 2.412e9
traceLength = 801
rsa.write('display:general:measview:new toverview')

rsa.write('spectrum:frequency:center {}'.format(cf))
rsa.write('initiate:continuous off')
rsa.write('trigger:status on')
rsa.write('trigger:event:source input')
rsa.write('trigger:event:input:type power')
rsa.write('trigger:event:input:level {}'.format(trigLevel))

analysisLength = 200e-6
spectrumLength = 7e-6
rsa.write('sense:spectrum:points:count {}'.format(traceLength))
rsa.write('sense:spectrum:time:mode independent')
rsa.write('sense:analysis:length {}'.format(analysisLength))
rsa.write('sense:spectrum:length {}'.format(spectrumLength))
#
offset = [o*1e-6 for o in range(25)]
inner = len(offset)
outer = length
print(length)

traces = []
# df = pd.DataFrame()
rsa.timeout = 10000
for i in range(outer-1):
    print('Acquisition ', i)
    rsa.write('initiate:immediate ')
    awg.write('trigger:immediate atrigger')
    try:
        rsa.query('*opc?')
        for o in offset:
            rsa.write('sense:spectrum:start {}'.format(o))
            rsa.write('sense:reanalyze:current')
            temp = rsa.query_binary_values('fetch:spectrum:trace1?',
                                             datatype='f')
            temp.append(1)
            traces.append(temp)
    except visa.VisaIOError:
        print('timed out, moving on')

    # plt.plot(spectrum)
    # plt.show()
outFileName = 'C:\\users\\mallison\\documents\\github\\visa_sandbox' \
              '\\traces_9-15-17_802.11n_3.csv'
print(np.shape(traces))
np.savetxt(outFileName, traces, delimiter=',')

try:
    rsa.close()
except:
    pass
try:
    awg.close()
except:
    pass