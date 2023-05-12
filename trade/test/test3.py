import threading
import pandas as pd
import time


data = {'state':['Ohio','Ohio','Ohio','Nevada','Nevada','Nevada'],
        'year':[2000,2001,2002,2003,2004,2005],
        'pop':[1.5,1.7,3.6,2.4,2.9,3.2]}
df = pd.DataFrame(data)

for row in df.itertuples():
        print(row.__getattribute__())
        print(row.__str__())

# for index, row in df.iterrows():
#         print(index)
#         print(row.to_string())
