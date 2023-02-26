import glob
import pprint
import os
import pandas as pd
import itertools


data_files = [file for file in glob.glob("data/*.csv")]
# pprint.pprint(data_files)
cols = [name.split("/")[1].split(".")[0] for name in data_files]
#pprint.pprint(cols)

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
    # dfs.append(df)

print(combined_df)

col_combinations = list(itertools.combinations(cols, 2))
# pprint.pprint(col_combinations)

results = {}
for col1, col2 in col_combinations:
    # print(combined_df[col1].apply(type))
    try:
        corr = combined_df[col1].corr(combined_df[col2])
    except Exception as e:
        print(e)
        print(col1, col2)
        print(combined_df[col1], combined_df[col2])
        break

    # print(f"correlation between {col1} and {col2}: {corr:.2f}")
    results[(col1, col2)] = float(f"{corr:.2f}")

# pprint.pprint(results)
# sorted_dict = dict(sorted(results.items(), key=lambda item: item[1]))
sorted_dict = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]

# pprint.pprint(sorted_dict)
# print(combined_df.corrwith(combined_df, axis=1))


ax1 = combined_df.plot.scatter(
        x='education_expenditures',
        y='birth_rate')


exit(0)

"""
ax1 = df.plot.scatter(
        x='infant_mortality_rate',
        y='population'
        )
"""
