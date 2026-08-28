import pandas as pd
from noteodps import ODPS, opt
from odps import DataFrame

print(opt.list_functions())

a = pd.DataFrame([[1, 2], [4, 6]])
a.columns = ['col1', 'col3']
print(a)
a2 = DataFrame(a)

a2.persist("local_test", partition="ds=20211101")
