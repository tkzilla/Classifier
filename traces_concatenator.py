import pandas as pd
import numpy as np

f1 = '802.11n_master_class1t.csv'
f2 = 'adds.csv'

data1 = pd.read_csv(f1).as_matrix()
data2 = pd.read_csv(f2).as_matrix()

print(data1.shape)
print(data2.shape)

data3 = np.concatenate((data1, data2), axis=0)

print(data3.shape)
np.savetxt('added_to_master.csv', data3, delimiter=',')
