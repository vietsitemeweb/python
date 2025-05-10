import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the processed data
data_file = 'results2.csv'
df = pd.read_csv(data_file)

# Check available columns in the dataset
print("Available columns in the dataset:", df.columns)

# Select relevant statistics for clustering
stats_to_cluster = [
    'Gls_mean', 'Ast_mean', 'xG_mean', 'xAG_mean', 'PrgC_mean', 'PrgP_mean'
]

# Filter only existing columns
stats_to_cluster = [col for col in stats_to_cluster if col in df.columns]
if not stats_to_cluster:
    raise ValueError("None of the specified columns for clustering exist in the dataset.")

# Select the data for clustering
df_cluster = df[stats_to_cluster].dropna()

# Standardize the data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(df_cluster)

# Determine the optimal number of clusters using the Elbow Method
inertia = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(data_scaled)
    inertia.append(kmeans.inertia_)

# Plot the Elbow Curve
plt.figure()
plt.plot(range(1, 11), inertia, marker='o')
plt.title('Elbow Method for Optimal K')
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.savefig('elbow_curve.png')
plt.close()

# Choose the optimal number of clusters (e.g., 3 based on the elbow curve)
optimal_k = 3
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df['Cluster'] = kmeans.fit_predict(data_scaled)

# Apply PCA to reduce dimensions to 2 for visualization
pca = PCA(n_components=2)
data_pca = pca.fit_transform(data_scaled)

# Plot the 2D clusters
plt.figure()
for cluster in range(optimal_k):
    cluster_points = data_pca[df['Cluster'] == cluster]
    plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {cluster}')
plt.title('Player Clusters (PCA)')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.savefig('player_clusters.png')
plt.close()

# Save the clustered data
df.to_csv('clustered_results.csv', index=False, encoding='utf-8-sig')