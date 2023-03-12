import glob
import pprint
import os
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import itertools
from constants import COLOURS, REGIONS


data_files = [file for file in glob.glob("data/*.csv")]
cols = [name.split("/")[1].split(".")[0] for name in data_files]
# print(cols)
# exit(0)

SPEARMAN = True
if SPEARMAN:
    METHOD = 'spearman'
    VALUE_COL = 'ranking'
    CONVERTERS = None
else:
    METHOD = 'pearson'
    VALUE_COL = 'value'
    CONVERTERS = {VALUE_COL: lambda s: float(s.replace(',', '').replace('$', ''))}

combined_df = None
for file in data_files:
    col_name = os.path.splitext(file)[0].split("/")[1]
    df = pd.read_csv(file,
            usecols = ['name', 'value', 'ranking'],
            converters = {
                'value': lambda s: float(s.replace(',', '').replace('$', '')),
                'rating': lambda s: int(s)
            }
            thousands=r',')

    df.columns = df.columns.str.strip()
    df = df[['name', 'value', 'rating']].rename(
        {'value': col_name,
         'rating': col_name + "_rt"
        }, axis=1)
    if combined_df is None:
        combined_df = df
        continue

    combined_df = pd.merge(combined_df, df, on='name', how='outer')

def region_code(row):
    # print(row)
    region = row['region']
    if region in REGIONS:
        return COLOURS[REGIONS.index(region)]
    return "gold"

# add regions etc.
region_df = pd.read_csv("more/regions.csv", usecols = ['name', 'region'])
df = pd.merge(combined_df, region_df, on='name', how='outer')

df['region_code'] = df.apply(lambda x : region_code(x), axis=1)


col_combinations = list(itertools.combinations(cols, 2))
random.shuffle(col_combinations)

THRESHOLD = 0.8
results = {}
for col1, col2 in col_combinations:
    try:
        corr = df[col1].corr(df[col2], method=METHOD)
    except Exception as e:
        # print(e)
        # print(col1, col2)
        # print(df[col1], df[col2])
        break
    if corr > -THRESHOLD and corr < THRESHOLD:
        continue
    if SPEARMAN:
        ax = df.plot.scatter(
            title=f'{col2} vs {col1}\n Ranking correlation: {corr:.2f}',
            x=col1,
            y=col2,
            c=df.region_code,
            figsize=(10,10))
    else:
        ax = df.plot.scatter(
            title=f'{col2} vs {col1}\nABS Value correlation: {corr:.2f}',
            x=col1,
            y=col2,
            c=df.region_code,
            s=df.population // 1_000_000,
            figsize=(10,10))
    for idx, row in df.iterrows():
        ax.annotate(row['name'], (row[col1], row[col2]), fontsize=8 )
    plt.show()
    plt.close()

    # print(f"correlation between {col1} and {col2}: {corr:.2f}")
    results[(col1, col2)] = float(f"{corr:.2f}")


sorted_dict = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]

print("Done.")




