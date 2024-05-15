# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime

from dash import dcc, html
from dateutil.relativedelta import relativedelta


#Configures the Dash Flask server
app = dash.Dash(__name__,meta_tags=[{'name':'viewport','content':'user-scalable=no'}])
server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True