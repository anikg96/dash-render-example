# Run this app with `python main.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
import json
import scanpy as sc
import pandas as pd

# Download the .h5ad file
import wget


h5ad_url = "https://h5adstorage.blob.core.windows.net/newcontainer/local.h5ad?sp=r&st=2022-12-21T13:31:30Z&se=2032-01-01T21:31:30Z&sv=2021-06-08&sr=b&sig=5pHKlcrCMOjMqSn0V3i0QF1RXW0doeyleOQxugofjdw%3D"
response = wget.download(h5ad_url, "Data/local.h5ad")

adata = sc.read_h5ad('Data/local.h5ad')
umap_df = pd.DataFrame(adata.obsm["X_umap"], columns=["UMAP_1", "UMAP_2"])

umap_df["cell_type"] = adata.obs["cell_type_original"].values

# The following two lines are very important.
# They are needed for changing the feature names from ENSG000___ to normal names
adata.var.reset_index(inplace=True)
adata.var.set_index('feature_name', inplace=True)

# Get the feature names
feature_names = adata.var.index.tolist()

# Create a data frame from the adata.X sparse matrix and label columns with feature names
x_dataframe = pd.DataFrame.sparse.from_spmatrix(adata.X, columns=feature_names)

# Finally join the sparse matrix columns with the initial dataframe containing UMAP and cell_type information
final_data = pd.concat([umap_df, x_dataframe],axis=1)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) # Initializes the app
server = app.server

# Example umap scatter plot
fig = px.scatter(final_data, x="UMAP_1", y="UMAP_2", color="cell_type")

app.layout = html.Div(children=[
    html.H1(children='SciViewer Python'),

    dcc.Graph(
        id='example-graph',
        figure=fig,
        style={'width': '120vh', 'height': '85vh'}
    ),

    html.Div(id='hover-data')
])

### Callbacks begin here ###

# Callback for getting the hover data from the graph
@app.callback(
    Output('hover-data', 'children'),
    Input('example-graph', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
