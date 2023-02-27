import glob
import pprint
import os
import pandas as pd
import matplotlib.pyplot as plt
import itertools


data_files = [file for file in glob.glob("data/*.csv")]
cols = [name.split("/")[1].split(".")[0] for name in data_files]

combined_df = None
for file in data_files:
    df = pd.read_csv(file,
            usecols = ['name', 'value'],
            converters={'value': lambda s: float(s.replace(',', '').replace('$', ''))},
            thousands=r',')

    # print(os.path.splitext(file)[0].split("/")[1])
    df.columns = df.columns.str.strip()
    df = df[['name', 'value']].rename({'value': os.path.splitext(file)[0].split("/")[1]}, axis=1)
    if combined_df is None:
        combined_df = df
        continue

    combined_df = pd.merge(combined_df, df, on='name', how='outer')

regions = {
    "Africa",
    "Australia and Oceania",
    "Central America and the Caribbean",
    "Central Asia",
    "East and Southeast Asia",
    "Europe",
    "Middle East",
    "North America",
    "South America",
    "South Asia"
}

# add regions etc.
region_df = pd.read_csv("more/regions.csv", usecols = ['name', 'region'])
df = pd.merge(combined_df, region_df, on='name', how='outer')
df['region'] = df['region'].astype('category')
region_labels = df['region'].unique()
pprint.pprint(region_labels)

print(df)
# exit(0)

col_combinations = list(itertools.combinations(cols, 2))

results = {}
for col1, col2 in col_combinations:
    try:
        corr = df[col1].corr(df[col2])
    except Exception as e:
        print(e)
        print(col1, col2)
        print(df[col1], df[col2])
        break
    if corr >= 0.9 or corr <= -0.9:
        pass
    ax = df.plot.scatter(
            x=col1,
            y=col2,
            c=region_labels.map(df.region),
            # cmap='viridis',
            s=50,
            figsize=(10,10))
    for idx, row in df.iterrows():
        ax.annotate(row['name'], (row[col1], row[col2]), fontsize=8 )
    plt.show()
    plt.close()
    break

    # print(f"correlation between {col1} and {col2}: {corr:.2f}")
    results[(col1, col2)] = float(f"{corr:.2f}")

# pprint.pprint(results)
# sorted_dict = dict(sorted(results.items(), key=lambda item: item[1]))
sorted_dict = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
# pprint.pprint(sorted_dict)
# exit(0)

print("Done.")




