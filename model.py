import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2

def fetch_data():
    conn = psycopg2.connect(
        host="localhost",
        database="shopify-reporting-app",
        user="postgres",
        password="Sairam_12345"
    )
    
    query = """
    SELECT * FROM "Customer" WHERE is_deleted = FALSE
    """
    data = pd.read_sql(query, conn)
    conn.close()
    
    return data

def main():
    data = fetch_data()

    print("Fetched Data:", data.head())
    print("Fetched Data Columns:", data.columns)

    required_columns = ['total_spent', 'orders_count', 'created_at', 'updated_at']
    for col in required_columns:
        if col not in data.columns:
            raise KeyError(f"Missing required column: {col}")

    data['total_spent'] = data['total_spent'].astype(float)
    data['orders_count'] = data['orders_count'].astype(int)
    data['created_at'] = pd.to_datetime(data['created_at'])
    data['updated_at'] = pd.to_datetime(data['updated_at'])
    data['updated_at'] = data['updated_at'].dt.tz_localize(None)

    data['average_order_value'] = data['total_spent'] / data['orders_count']
    data['recency'] = (pd.Timestamp.now() - data['updated_at']).dt.days

    features = data[['orders_count', 'total_spent', 'average_order_value', 'recency']]

    if features.isnull().values.any():
        print("Data contains NaN values.")
        features = features.fillna(0)

    if np.isinf(features.values).any():
        print("Data contains infinity values.")
        features.replace([np.inf, -np.inf], 0, inplace=True)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)
    data['cluster'] = clusters

    # Filter out non-numeric columns before grouping
    numeric_columns = data.select_dtypes(include=[np.number])
    cluster_analysis = numeric_columns.groupby(data['cluster']).mean()

    cluster_counts = data['cluster'].value_counts().sort_index()
    cluster_analysis['count'] = cluster_counts
    print(cluster_analysis)

    palette = sns.color_palette('viridis', n_colors=5)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='total_spent', y='orders_count', hue='cluster', data=data, palette=palette, legend=None)

    handles = []
    for cluster, count in cluster_counts.items():
        handles.append(plt.Line2D([0], [0], marker='o', color='w', label=f'Cluster {cluster} (Count: {count})',
                                  markerfacecolor=palette[cluster], markersize=10))

    plt.legend(title='Clusters', handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize='small', title_fontsize='medium')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.title('Customer Segmentation')
    plt.xlabel('Total Spend')
    plt.ylabel('Orders Count')
    plt.show()

if __name__ == '__main__':
    main()
