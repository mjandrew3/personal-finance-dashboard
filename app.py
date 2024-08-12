# -*- coding: utf-8 -*-

import dash


#Configures the Dash Flask server
app = dash.Dash(__name__,meta_tags=[{'name':'viewport','content':'user-scalable=no'}])
server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True