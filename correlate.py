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
                'ranking': lambda s: int(s)
            },
            thousands=r',')

    df.columns = df.columns.str.strip()
    df = df[['name', 'value', 'ranking']].rename(
        {'value': col_name,
         'ranking': col_name + "_r"
        }, axis=1)
    # reverse the ranking
    # df[col_name + "_r"] = range(len(df), 0, -1)
    # df.drop('ranking', axis=1)
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
# random.shuffle(col_combinations)

THRESHOLD = 0.8
results = {}
for col1, col2 in col_combinations:
    # print(col1, col2)
    TITLE = f"{col2} vs {col1}"
    CHART_FILENAME = "charts/" + TITLE.replace(' ', '_') + ".png"
    if os.path.isfile(CHART_FILENAME):
        print(f"skipping {TITLE}")
        continue
    col1_r = col1 + "_r"
    col2_r = col2 + "_r"
    try:
        corr1 = df[col1].corr(df[col2], method='pearson')
        corr2 = df[col1_r].corr(df[col2_r], method='spearman')
    except Exception as e:
        # print(e)
        # print(col1, col2)
        # print(df[col1], df[col2])
        break
    if (corr1 > -THRESHOLD and corr1 < THRESHOLD) and  \
       (corr2 > -THRESHOLD and corr2 < THRESHOLD):
        continue
    print(f"processing {TITLE}")

    fig = plt.figure(figsize=(14,8))
    fig.suptitle(TITLE, fontsize=12)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    # Value correlation
    ax1.scatter(
        df[col1],
        df[col2],
        c=df.region_code,
        s=df.population // 1_000_000
        )
    ax1.set_title(f'ABS: c={corr1:.2f}')
    ax1.set_xlabel(col1)
    ax1.set_ylabel(col2)

    # Raking correlation
    ax2.scatter(
        df[col1_r],
        df[col2_r],
        c=df.region_code
    )
    ax2.set_title(f'RANK: c={corr2:.2f}')
    ax2.set_xlabel(col1_r)
    ax2.set_ylabel(col2_r)
    ax2.invert_xaxis()
    ax2.invert_yaxis()

    for idx, row in df.iterrows():
        ax1.annotate(row['name'], (row[col1], row[col2]), fontsize=8 )
        ax2.annotate(row['name'], (row[col1_r], row[col2_r]), fontsize=8 )
    # plt.show()
    fig.savefig(CHART_FILENAME, dpi=fig.dpi)
    plt.close()

    results[(col1, col2)] = float(max(abs(corr1), abs(corr2)))


sorted_dict = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
pprint.pprint(sorted_dict)

print("Done.")




