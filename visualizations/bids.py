from cmath import nan
from sys import maxsize
import pandas as pd
import numpy as np
import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from os.path import dirname, join

current_dir = dirname(__file__)
file_path = join(current_dir, "./bids.csv")
df = pd.read_csv(file_path)

cf.go_offline()
cf.set_config_file(theme="solar")

fig = make_subplots(cols=2)

customdata = np.stack((df["strategy_activate_ltv"], df["strategy_activate_amount"]/1000000), axis=-1)
hovertemplate=("Borrow Limit Threshold: %{customdata[0]}%<br>" + "At-Risk Collateral Threshold: %{customdata[1]}m<br>")
size = []
for i in df["amount"]:
    if np.isnan(i):
        break
    a = 0
    i_str = str(i).replace(".","")
    for j, k in enumerate(reversed(i_str)):
        a += j*int(k)
    else:
        size.append(a)
scatter = go.Scatter(x=df["premium_slot"], y=df["amount"], mode="markers", marker={"size": size})
fig.add_trace(scatter, row=1, col=1)
fig.update_traces(row=1, col=1, customdata=customdata, hovertemplate=hovertemplate)
fig.update_layout(
    xaxis={"title": "Premium", "tickformat": "0%"},
    yaxis={"title": "Pool Value (aUST)"},
)

customdata = np.stack((df["premium_slot"], df["amount"]/1000), axis=-1)
hovertemplate = ("Premium: %{customdata[0]}%<br>" + "Amount: %{customdata[1]}k<br>")
size = [i / 100000 for i in df["strategy_activate_amount"]]
scatter = go.Scatter(x=df["strategy_activate_ltv"], y=df["strategy_activate_amount"], mode="markers", marker={"size": size})
fig.add_trace(scatter, row=1, col=2)
fig.update_traces(row=1, col=2, customdata=customdata, hovertemplate=hovertemplate)
fig.update_layout(
    xaxis2={"title": "Borrow Limit Threshold", "tickformat": "0%"},
    yaxis2={"title": "At-Risk Collateral Threshold"},
)

fig.show()