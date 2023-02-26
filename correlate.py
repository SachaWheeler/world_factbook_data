import glob
import pprint
import os
import pandas as pd


data_files = [file for file in glob.glob("data/*.csv")]
# pprint.pprint(data_files)

combined_df = None
for file in data_files:
    df = pd.read_csv(file, usecols = ['name', 'value'])

    # print(os.path.splitext(file)[0].split("/")[1])
    df.columns = df.columns.str.strip()
    df = df[['name', 'value']].rename({'value': os.path.splitext(file)[0].split("/")[1]}, axis=1)
    if combined_df is None:
        combined_df = df
        continue

    combined_df = pd.merge(combined_df, df, on='name', how='outer')
    # dfs.append(df)

print(combined_df)
exit(0)
pprint.pprint(dfs)
# df = cols[0]
# for sub_df in cols[1:]:
    # df = df.merge(sub_df, on='residue')
