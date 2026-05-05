import pandas as pd

def load_file(file):
    return pd.read_csv(file, sep='|', engine='python')
