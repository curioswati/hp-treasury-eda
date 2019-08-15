#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np


# In[2]:


from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize, Normalizer, StandardScaler
from sklearn.pipeline import make_pipeline
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster


# In[3]:


import wrangler
import utils


# In[ ]:


filename = '01._Receipt_-_DDOReceipt_Head_Date_and_Challan_Wise.csv'
filepath = utils.get_munged_filepath(filename)
df = pd.read_csv(filepath, parse_dates=True)
df = wrangler.wrangle_data_for_receipt(df, ['RECEIPTHEAD'])


# In[4]:


file = '10._Expenditure_-_DDO_Head_of_AccountSOE_and_VoucherBillNO_wise.csv'
filepath = utils.get_munged_filepath(file)
df = pd.read_csv(filepath, parse_dates=True)
df = wrangler.wrangle_data_for_consolidated_query(df, ['DDODESC', 'DISTRICT', 'TREASURY', 'DDO'])


# In[ ]:


data = df.groupby('DISTRICT',).sum()
samples = data.loc[:, ['AGDED', 'BTDED', 'NETPAYMENT']].values


# In[ ]:


# finding optimal k, select the k using elbow method from the plot
ks = np.arange(1, 11)
inertias = []
for k in ks:
    model = KMeans(n_clusters=k)
    model.fit(samples)
    inertias.append(model.inertia_)
plt.scatter(ks, inertias)
plt.show()


# In[ ]:


# t-SNE method to plot dataset with multiple dimensions. t-SNE reduces the data to two dimensions.
# Import TSNE
from sklearn.manifold import TSNE

# Create a TSNE instance: model
model = TSNE(learning_rate=50)

# Apply fit_transform to normalized_movements: tsne_features
tsne_features = model.fit_transform(normalize(samples))

# Select the 0th feature: xs
xs = tsne_features[:, 0]

# Select the 1th feature: ys
ys = tsne_features[:,1]

# Scatter plot
plt.scatter(xs, ys, alpha=0.5)

# Annotate the points
for x, y, district in zip(xs, ys, data.index.values):
    plt.annotate(district, (x, y), fontsize=5, alpha=0.75)
plt.show()


# In[ ]:


# use pipeline to get labels for samples
scaler = Normalizer()
model = KMeans(n_clusters=2)
pipeline = make_pipeline(scaler, model)
pipeline.fit(samples)
labels = pipeline.predict(samples)


# In[ ]:


# reduce clusters in hierarchical clustering with fcluster to get crosstab like k-Means clustering.
normalized_samples = normalize(samples)
mergings = linkage(normalized_samples, method='single')
labels = fcluster(mergings, 0.02, criterion='distance')
# dendrogram(mergings,
#          labels=data.index.values,
#          leaf_rotation=90,
#          leaf_font_size=6)
# plt.show()
result = pd.DataFrame({'labels': labels, 'districts': data.index.values}, columns=['labels', 'districts'])
ct = pd.crosstab(result['labels'], result['districts'])
print(ct)


# In[ ]:


# hierarchical clustering using linkage and dendrograms
normalized_samples = normalize(samples)
mergings = linkage(normalized_samples, method='complete')
dendrogram(mergings,
         labels=data.index.values,
         leaf_rotation=90,
         leaf_font_size=6)
plt.show()


# In[ ]:


# compute crosstab for labels and targets
result = pd.DataFrame({'labels': labels, 'districts': data.index.values}, columns=['labels', 'districts'])
ct = pd.crosstab(result['labels'], result['districts'])
print(ct)


# In[5]:


# building word frequency matrix
from sklearn.feature_extraction.text import TfidfVectorizer

documents = df.DDODESC.unique()
tfidf = TfidfVectorizer()
csr_mat = tfidf.fit_transform(documents).toarray()
words = tfidf.get_feature_names()


# In[ ]:


# use truncatedsvd to make clusters for word frequency data.
# here we use truncatedsvd as a replacement to PCA for sparse matrix data.
# It's job is to reduce dimensions as PCA do.
from sklearn.decomposition import TruncatedSVD

# Create a TruncatedSVD instance: svd
svd = TruncatedSVD(n_components=50)

# Create a KMeans instance: kmeans
kmeans = KMeans(n_clusters=6)

# Create a pipeline: pipeline
pipeline = make_pipeline(svd, kmeans)

# Fit the pipeline to articles
pipeline.fit(csr_mat)

# Calculate the cluster labels: labels
labels = pipeline.predict(csr_mat)

# Create a DataFrame aligning labels and titles: df
new_df = pd.DataFrame({'label': labels, 'indices': documents})

# Display df sorted by cluster label
print(new_df.sort_values(by='label'))


# In[6]:


# use NMF for dimension reduction.
from sklearn.decomposition import NMF

# Create an NMF instance: model
model = NMF(n_components=6)

# Fit the model to articles
model.fit(csr_mat)

# Transform the articles: nmf_features
nmf_features = model.transform(csr_mat)

# Print the NMF features
print(nmf_features)


# In[10]:


# recommender system with NMF

norm_features = normalize(nmf_features)
new_df = pd.DataFrame(norm_features, index=documents)
ddo = new_df.loc['PRINCIPAL GOVT. DEGREE COLLEGE KHAD']
similar = new_df.dot(ddo)
print(similar.nlargest())

