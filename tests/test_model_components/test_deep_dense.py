import string
import numpy as np
import torch
import pytest

from pytorch_widedeep.models import DeepDense

colnames = list(string.ascii_lowercase)[:10]
embed_cols = [np.random.choice(np.arange(5), 10) for _ in range(5)]
cont_cols = [np.random.rand(10) for _ in range(5)]

X_deep = torch.from_numpy(np.vstack(embed_cols+cont_cols).transpose())
X_deep_emb = X_deep[:, :5]
X_deep_cont = X_deep[:, 5:]

###############################################################################
# Embeddings and NO continuous_cols
###############################################################################
embed_input = [(u,i,j) for u,i,j in zip(colnames[:5], [5]*5, [16]*5)]
model1 = DeepDense(
    hidden_layers=[32,16],
    dropout=[0.5],
    deep_column_idx={k:v for v,k in enumerate(colnames[:5])},
    embed_input=embed_input,
    output_dim=1)

def test_deep_dense_embed():
	out = model1(X_deep_emb)
	assert out.size(0) == 10 and out.size(1) == 1

###############################################################################
# Continous cols but NO embeddings
###############################################################################
continuous_cols=colnames[-5:]
model2 = DeepDense(
hidden_layers=[32,16],
dropout=[0.5],
deep_column_idx={k:v for v,k in enumerate(colnames[5:])},
continuous_cols=continuous_cols,
output_dim=1)

def test_deep_dense_cont():
	out = model2(X_deep_cont)
	assert out.size(0) == 10 and out.size(1) == 1

###############################################################################
# Continous Cols and Embeddings
###############################################################################
model3 = DeepDense(
hidden_layers=[32,16],
dropout=[0.5],
deep_column_idx={k:v for v,k in enumerate(colnames)},
embed_input=embed_input,
continuous_cols=continuous_cols,
output_dim=1)

def test_deep_dense():
	out = model3(X_deep)
	assert out.size(0) == 10 and out.size(1) == 1