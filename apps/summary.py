# -*- coding: utf-8 -*-
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable, FormatTemplate
from dash.dependencies import Input, Output, State
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from io import StringIO

from app import app
from utils import get_data, get_options, generate_table, generate_graph


#Get Income and Expense data for Actual and Budget
total_data = get_data('total')
total_data = total_data.groupby(['Category Type','YearMonth'],as_index=False)['Amount'].sum()
budget_data = get_data('budget').groupby(['Category Type','YearMonth'],as_index=False)['Amount'].sum()
budget_data['Type Detail'] = 'Budget'
invest = get_data('invest').groupby('YearMonth',as_index=False)['Transfers'].sum()
invest['Transfers'] = invest['Transfers'] * -1
invest['Category Type'] = 'Other'
total_data = pd.concat([total_data,invest.rename(columns={'Transfers':'Amount'})])
total_data['Type Detail'] = 'Actual'
total_data = pd.concat([total_data,budget_data])

layout = html.Div([
            html.A('Display', id='s-icon', className='icon', n_clicks=1),
            html.Div([
                dbc.Select(value=(datetime.date.today()-datetime.timedelta(datetime.date.today().day)).strftime('%Y-%m'), options=get_options(sorted(total_data['YearMonth'].unique()),'1'),   
                           id='s-date1', className='select'),
                dbc.Select(value=(datetime.date.today()-datetime.timedelta(datetime.date.today().day)).strftime('%Y-%m'), options=get_options(sorted(total_data['YearMonth'].unique()),'1'),
                           id='s-date2', className='select'),
                dbc.Select(value='Aggregate By: Sum', options=get_options(['Aggregate By: Sum','Aggregate By: Average'],'1'),
                           id='s-view', className='select'),
                html.Button('Apply Filters',id='s-apply', style={'align':'center'}, className='apply', n_clicks=0),
                dcc.Store(id='s-store',storage_type='local')
            ], id='s-topnav', className='t-topnav'),
        html.Div(id='s-mobile-page-content')
        
        ],className='wrapper')

@app.callback(Output('s-topnav','style'),
              [Input('s-icon','n_clicks')])
def show1(clicks):
    '''Hide and Show the topnav bar
    '''
    if ((clicks % 2 != 0) or (clicks == 0)) and (clicks != 1):
        return {'display':'block'}
    else:
        return {'display':'none'}

@app.callback(Output('s-store','data'),
              [Input('s-apply','n_clicks')],
               [State('s-store','data'),
                State('s-view','value'),
                State('s-date1','value'),
                State('s-date2','value')])
def update_store(click,data,view_value,date1_value,date2_value):
    '''Use a cache store to store details of the current config
    '''
    from pandas import read_json
    if data == None:
        data = pd.DataFrame([[click,view_value,date1_value,date2_value]],
                            columns=['s-apply','s-view','s-date1','s-date2'])
    else:
        data = read_json(StringIO(data))[['s-apply','s-view','s-date1','s-date2']]
        data = pd.concat([data,pd.DataFrame([[click,view_value,date1_value,date2_value]],
                                            columns=['s-apply','s-view','s-date1','s-date2'])]).reset_index(drop=True)
        data = data.iloc[-2:]
    return data.to_json()


@app.callback(Output('s-mobile-page-content','children'),
              [Input('s-store','data')])
def show_content(data):
    '''From the cache store, process and display the main table
    '''
    from pandas import read_json
    data = read_json(StringIO(data))[['s-apply','s-view','s-date1','s-date2']]
    click,view_value,date1_value,date2_value = data.iloc[-1]
    
    total_data1 = total_data[(total_data['YearMonth']>=date1_value)&(total_data['YearMonth']<=date2_value)]
    num_months = relativedelta(datetime.date(int(date2_value[:4]),int(date2_value[5:]),1),
                               datetime.date(int(date1_value[:4]),int(date1_value[5:]),1)).months+1
    total_data1 = total_data1.groupby(['Type Detail','Category Type'],as_index=False)['Amount'].sum()
    if view_value == 'Aggregate By: Average':
        total_data1['Amount'] = total_data1['Amount'] / num_months
    total_data1 = total_data1.pivot(index='Category Type',columns='Type Detail',values='Amount')
    total = pd.DataFrame(total_data1.sum(),columns=['Savings']).T
    total_data1 = pd.concat([total_data1,total])
    total_data1['Difference'] = np.where(total_data1.index=='Savings',
                                         total_data1['Actual'] - total_data1['Budget'],
                                         total_data1['Actual'].abs() - total_data1['Budget'].abs())
    total_data1 = total_data1.reset_index(drop=False).rename(columns={'index':'Type Detail'})
    total_data1['Type Detail'] = pd.Categorical(total_data1['Type Detail'],['Income','Expense','Other','Savings'])
    
    columns_ = [dict(id='Type Detail',name='Type Detail',presentation='markdown'),
                dict(id='Actual',name='Actual',type='numeric',format=FormatTemplate.money(0)),
                dict(id='Budget',name='Budget',type='numeric',format=FormatTemplate.money(0)),
                dict(id='Difference',name='Difference',type='numeric',format=FormatTemplate.money(0))]
    data_ = total_data1.sort_values(by='Type Detail').to_dict(orient='records')
    data_[0]['Type Detail'] = '[Income](?t=income&start=' + date1_value +'&end=' + date2_value + ')'
    data_[1]['Type Detail'] = '[Expense](?t=expense&start=' + date1_value +'&end=' + date2_value + ')'
    data_[2]['Type Detail'] = '[Other](?t=investment&start=' + date1_value +'&end=' + date2_value + ')'
    data_[3]['Type Detail'] = '[Savings](?t=budget&start=' + date1_value +'&end=' + date2_value + ')'

    table = DataTable(id='table',columns=columns_,data=data_,markdown_options={'link_target':'_self'},style_data_conditional=[
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} > 0 and {Type Detail} = '[Income](?t=income&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'green'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} < 0 and {Type Detail} = '[Income](?t=income&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'red'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} < 0 and {Type Detail} = '[Expense](?t=expense&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'green'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} > 0 and {Type Detail} = '[Expense](?t=expense&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'red'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} > 0 and {Type Detail} = '[Other](?t=investment&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'green'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} < 0 and {Type Detail} = '[Other](?t=investment&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'red'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} > 0 and {Type Detail} = '[Savings](?t=budget&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'green'},
            {'if':{'column_id':['Difference','Type Detail'],
                   'filter_query':"{Difference} < 0 and {Type Detail} = '[Savings](?t=budget&start=" + date1_value + '&end=' + date2_value + ")'"},
                   'color': 'red'}
            ],
    style_cell={'textAlign':'center','fontSize':30,'fontFamily':'sans-serif'})
    layout = html.Div([table])
    return layout


def test_variables():
    '''Variables used to test the front end
    '''
    click=0
    view_value = 'Aggregate By: Sum'
    date1_value = '2024-01'
    date2_value = '2024-07'
    return click, view_value, date1_value, date2_value
