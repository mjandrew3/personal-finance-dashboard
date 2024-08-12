# -*- coding: utf-8 -*-

from dash import dcc, html, callback_context
from dash.dependencies import Input, Output

from app import app
from apps import account,actual,budget,detail,expense,income,investment,summary


# Initial App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), # Allows the use of the url
    html.Div(id='page-content', children=[
        html.Div([
            html.A('Personal Finance Application', id='icon', n_clicks=1, className='icon'),
            html.Div(
                #Creates tabs at the top of the page for easy navigation
                [dcc.Tabs(id='tabs',children=[
                dcc.Tab(label='Summary',value='summary'),
                dcc.Tab(label='Details',value='detail'),
                dcc.Tab(label='Investing',value='invest'),
                dcc.Tab(label='Accounts',value='account')
            ],className='tabs')
	], className='topnav', id='topnav'),
        #Allows a Loading icon to show the app is working
        dcc.Loading(
            html.Div(id='mobile-page-content'),
            id='loading-1',
            fullscreen=True,
            style={'vertical-align':'top'},
            className='_dash-loading-callback')
        ])
    ])
])


@app.callback([Output('mobile-page-content', 'children'),
               Output('icon','children'),
               Output('icon','n_clicks'),
               Output('url','pathname')],
              [Input('url','search'),
               Input(component_id='tabs',component_property='value')])
def display_page(url,tabvalue):
    '''This takes 2 types of inputs, the URL and a tab value.  Both of these
can be updated and trigger this callback, which changes the layout of the page 
based on which tab is clicked or what url is visited.

    '''
    if callback_context.triggered[0]['prop_id'] == 'url.search':
        url_output = url
    else:
        url_output = ''
    if tabvalue == 'summary':
        return summary.layout,'Summary',0, url_output
    elif tabvalue == 'detail':
        return detail.layout,'Details',0, url_output
    elif tabvalue == 'invest':
        return investment.layout, 'Investing',0, url_output
    elif tabvalue == 'account':
        return account.layout, 'Accounts',0, url_output
    elif url.split("&")[0] == '?t=e':
        return expense.layout, 'Expense vs Budget',0, url_output
    elif url.split("&")[0] == '?t=inc':
        return income.layout, 'Income vs Budget',0, url_output
    elif url.split("&")[0] == '?t=inv':
        return investment.layout, 'Investing',0, url_output
    elif url.split("&")[0] == '?t=b':
        return budget.layout, 'Budget',0, url_output
    else:
        return '','Please select a tab',1, url_output

@app.callback(Output('tabs','style'),[
              Input('icon','n_clicks')])
def show(clicks):
    '''This shows and hides the navigation page depending on how 
many times it's clicked.
    
    '''
    if clicks % 2 == 0:
        return {'display':'none'}
    else:
        return {'display':'block'}

if __name__ == '__main__':
    '''When called and run directly, this will spin up the server to host the app.
    
    '''
    app.run_server(host='0.0.0.0', dev_tools_hot_reload=True)
