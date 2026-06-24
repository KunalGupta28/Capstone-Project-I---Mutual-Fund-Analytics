import sys
# Inject the roaming packages directory where pandas and numpy are already installed
sys.path.insert(0, r"C:\Users\Dell\AppData\Roaming\Python\Python313\site-packages")

import pandas as pd
import numpy as np
print("Python Executable:", sys.executable)
print("Pandas Version:", pd.__version__)
print("Numpy Version:", np.__version__)
