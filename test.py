import pandas as pd
import random

a = {'A':[0, 1, 0, 1, 1], 'B':[0, 0, 1, 0, 1]}
b = {'A':[random.randint(1, 10) for i in range(5)], 'B':[random.randint(1, 10) for i in range(5)]}


a = pd.DataFrame(a)
b = pd.DataFrame(b)

c = b[a == 1].stack()
cc = b[a == 1].stack()
ccc = b[a == 1].stack()

res = pd.concat([c, cc, ccc], axis=1)
res.columns = ['c', 'cc', 'ccc']

imax = res['c'].idxmax()

res = pd.Series(res.iloc[imax[0]])

res = res.append(pd.Series(res.name))



a = {'A':[1,2,3,4,5]}
res = pd.DataFrame(a, index=['a', 'b', 'c', 'd', 'e'])
# res.set_index(['a', 'b', 'c', 'd', 'e'], inplace=True)
print(res.loc['a'])