import pandas as pd
import numpy as np

df = pd.read_csv('Megabonk GSC3月月度数据_无标题页面_表格.csv')

# The columns are: Date,Query,Landing Page,Impressions,Average Position,Url Clicks,URL CTR
# Convert impressions and clicks to numeric safely
df['Impressions'] = pd.to_numeric(df['Impressions'], errors='coerce').fillna(0)
df['Url Clicks'] = pd.to_numeric(df['Url Clicks'], errors='coerce').fillna(0)
df['Average Position'] = pd.to_numeric(df['Average Position'], errors='coerce').fillna(100)

# Aggregate by Query and Landing Page
agg_df = df.groupby(['Query', 'Landing Page']).apply(
    lambda x: pd.Series({
        'Impressions': x['Impressions'].sum(),
        'Clicks': x['Url Clicks'].sum(),
        'Position': np.average(x['Average Position'], weights=x['Impressions']) if x['Impressions'].sum() > 0 else x['Average Position'].mean(),
    })
).reset_index()

agg_df['CTR'] = (agg_df['Clicks'] / agg_df['Impressions']).fillna(0)

# Sort by Impressions
agg_df = agg_df.sort_values(by='Impressions', ascending=False)
agg_df.to_csv('aggregated_gsc.csv', index=False)

# Also aggregate purely by query
query_agg = df.groupby('Query').apply(
    lambda x: pd.Series({
        'Impressions': x['Impressions'].sum(),
        'Clicks': x['Url Clicks'].sum(),
        'Position': np.average(x['Average Position'], weights=x['Impressions']) if x['Impressions'].sum() > 0 else x['Average Position'].mean(),
        'LandingPages': x['Landing Page'].nunique(),
        'TopLandingPage': x.groupby('Landing Page')['Impressions'].sum().idxmax()
    })
).reset_index()

query_agg['CTR'] = (query_agg['Clicks'] / query_agg['Impressions']).fillna(0)
query_agg = query_agg.sort_values(by='Impressions', ascending=False)
query_agg.to_csv('query_agg.csv', index=False)

print(f"Total Unique Queries: {len(query_agg)}")
print(query_agg.head(50).to_string())
