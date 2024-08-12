
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime

from dash import dcc, html
from dateutil.relativedelta import relativedelta

def file_read(filename):
    '''Reads in file and handles exceptions if not available.
    
    '''
    try:
        file = pd.read_csv(filename)
    except FileNotFoundError:
        print("File not found.  Please include the file:",filename)
        return pd.DataFrame()
    except:
        print("File opening error. Please correct the issue.")
        return pd.DataFrame()
    return file

def get_data(type_='total'):
    '''Imports data depending on which section you're in
    
    '''
    #Read in necessary files
    budget_file = file_read("datasets/budget.csv")
    spend_file = file_read("datasets/spend.csv")
    spend_file['Type Detail'] = spend_file['Type Detail'].fillna("[" + spend_file['Account'] + ']')
    hierarchy_file = file_read("datasets/hierarchy.csv")

    #Process files for app
    original_file = spend_file.merge(hierarchy_file, 'left', 'Type Detail')
    original_file['Dummy'] = 'Dummy'
    original_file['Amount'] = original_file['Amount'].astype(str).str.replace(",","").astype(float).round(2)
    original_file['YearMonth'] = pd.to_datetime(original_file['Date Applied'], format='%Y-%m-%d').dt.strftime('%Y-%m')
    original_file['Type Detail'] = np.where(original_file['Type Detail'].str[:5]=='Other',
                                    original_file['Type'] + ":" + original_file['Type Detail'],
                                    original_file['Type Detail'])
    spend_file = original_file[original_file['Category']=='Income/Expense']
    #yearmonth = [{'label':x.strftime('%Y-%m'),'value':x.strftime('%b %Y')} for x in list(pd.to_datetime(spend_file['Date Applied']).dt.to_period('M').sort_values().unique())]
    
    if type_ == 'budget':
        budget_file['Category'] = 'Budget'
        budget_file['Date Applied'] = pd.to_datetime(budget_file['Date'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')
        budget_file['YearMonth'] = pd.to_datetime(budget_file['Date'], format='%Y-%m-%d').dt.strftime('%Y-%m')
        budget_file['Amount'] = budget_file['Amount'].astype(str).str.replace(",","").str.replace("$","").str.replace("`","0").astype(float).round(2)
        budget_file = budget_file.merge(spend_file[['Type','Type Detail','Category Type','Frequency','Dummy']].drop_duplicates(), on='Type Detail', how='left')
        budget_file['Type'] = budget_file['Type'].fillna('Other')
        budget_file['Category Type'] = budget_file['Category Type'].fillna('Other')
        budget_file['Frequency'] = budget_file['Frequency'].fillna('Monthly')
        budget_file['Dummy'] = budget_file['Dummy'].fillna('Dummy')
        return budget_file
    elif type_ == 'total':
        return spend_file
    elif type_ == 'invest':
        invest_file = file_read("datasets\investment.csv")
        invest_file['YearMonth'] = (pd.to_datetime(invest_file['Date'], format='%Y-%m-%d')).dt.strftime('%Y-%m')
        return invest_file
    elif type_ == 'account':
        return original_file
    elif type_ == 'hierarchy':
        return hierarchy_file
    else:
        spend_file_new = spend_file.append(budget_file[['Type Detail','Amount','Type','YearMonth','Category Type','Dummy','Category','Frequency','Date Applied']].drop_duplicates())
        return spend_file_new
    
def string_to_dict(url):
    url = url[1:].split('&')
    url_dict = {}
    if url != ['']:
        for x in url:
            url_dict[x.split('=')[0]]=x.split('=')[1]
    return url_dict
    
def get_options(all_options,total=None,sort=True):
    if total == None:
        if sort:
            options = [{'label':'Total','value':'Total'}] + [{'label':x,'value':x} for x in sorted(all_options)]
        else:
            options = [{'label':'Total','value':'Total'}] + [{'label':x,'value':x} for x in all_options]
    else:
        if sort:
            options = [{'label':x,'value':x} for x in sorted(all_options)]
        else:
            options = [{'label':x,'value':x} for x in all_options]
    return options

def generate_table(df,columns=['Type','Category Type'],date_var='YearMonth',amount_var='Amount',agg_type='sum',inc_date=True, num_months=1,sort_by='Categories',month_value='full'):
    if inc_date == False:
        agg_columns = columns[:]
    else:
        agg_columns = columns + [date_var]
    df[amount_var] = df[amount_var].fillna(0)
    df = df.fillna('').groupby(agg_columns,as_index=False).agg({amount_var:'sum'})
    if 'Category' in columns:
        new_data = df.groupby(agg_columns,as_index=False).agg({amount_var:'sum'})
        columns = [x for x in agg_columns if x != 'Category']
        if inc_date==False:
            new_data[amount_var] = np.where(sorted(new_data['Category'].unique())==['Budget','Income'],new_data[amount_var] * -1,new_data[amount_var])
            new_data[amount_var] = np.where(new_data['Category'].isin(['Income','Expense']),new_data[amount_var]*-1,new_data[amount_var])
            new_data = new_data.pivot_table(index=columns,columns='Category',values='Amount').fillna(0).reset_index()
            if 'Budget' not in new_data.columns:
                new_data['Budget'] = 0
            new_data['Difference'] = new_data[new_data.columns[-2]]+new_data[new_data.columns[-1]]
            amount_var = list(new_data.columns[-3:])
            agg_values = {x:'sum' for x in amount_var}
            df_total = pd.DataFrame([new_data.agg(agg_values)])
            for x in range(len(columns)):
                df_temp = new_data.groupby(by=columns[:x+1],as_index=False).agg(agg_values)
                df_total = df_total.append(df_temp)
            df_total[amount_var] = df_total[amount_var] / num_months
            if sort_by == 'Categories':
                df_total = df_total.fillna("AAAATotal")[columns+amount_var].sort_values(by=columns, ascending=True).replace("AAAATotal","Total")
            else:
                df_total = df_total.fillna("Total")[columns+amount_var].sort_values(by='Difference', ascending=False)
            if "Expense" in df_total.columns:
                df_total['Expense'] = df_total['Expense'] * -1
            else:
                df_total['Budget'] = df_total['Budget'] * -1
        else:
            if agg_type == 'sum':
                df_total = new_data.pivot_table(index=[x for x in agg_columns if x not in ['Category','YearMonth']]+['Category'],columns='YearMonth',values='Amount').fillna(0).reset_index()
            else:
                if 'Expense' in new_data['Category'].unique():
                    cat_var = 'Expense'
                else:
                    cat_var = 'Income'
                new_data = new_data.pivot_table(index=columns,columns='Category',values='Amount').fillna(0).reset_index()
                new_data['Current Month'] = np.where(new_data['YearMonth'].max()==new_data['YearMonth'],new_data[cat_var],0)
                new_data['Budget'] = np.where(new_data['YearMonth'].max()==new_data['YearMonth'],new_data['Budget'],0)
                new_data[cat_var] = np.where(new_data['YearMonth'].max()!=new_data['YearMonth'],new_data[cat_var],0)
                max_date = new_data[new_data[cat_var]!=0]['YearMonth'].max()
                min_date = new_data[new_data[cat_var]!=0]['YearMonth'].min()
                num_months = relativedelta(datetime.date(int(max_date[:4]),int(max_date[5:]),1),datetime.date(int(min_date[:4]),int(min_date[5:]),1)).months+1
                df_total = new_data.groupby([x for x in columns if x != 'YearMonth'], as_index=False)[new_data.columns[-3:]].sum()
                df_total = df_total[list(df_total.columns[:-3])+[cat_var,'Budget','Current Month']]
                df_total[cat_var] = df_total[cat_var] / num_months
                if sort_by!='Categories':
                    df_total = df_total.sort_values(by='Current Month')
    else:
        df_total = pd.DataFrame([df.agg({amount_var:'sum'})])
        for x in range(len(columns)):
            df_temp = df.groupby(by=columns[:x+1],as_index=False).agg({amount_var:'sum'})
            df_temp[amount_var] = df_temp[amount_var]
            df_total = df_total.append(df_temp)
        df_total[amount_var] = df_total[amount_var] / num_months
        if sort_by == 'Categories':
            df_total = df_total.fillna("AAAATotal")[agg_columns+[amount_var]].sort_values(by=agg_columns, ascending=True).replace("AAAATotal","Total")
        else:
            df_total = df_total.fillna("AAAATotal")[agg_columns+[amount_var]].sort_values(by=amount_var, ascending=False).replace("AAAATotal","Total")
    table = dbc.Table.from_dataframe(df_total.fillna("Total"), float_format=',.0f', bordered=True, striped=True, dark=True, hover=True, responsive=True)
    return table

def generate_graph(df,column='Type',date_var='YearMonth',amount_var='Amount',diff=True,diff_column='Type'):
    
    graph_data = [go.Bar(name=z, x = df[df[column]==z]['YearMonth'],
                        y = df[df[column]==z]['Amount']) for z in df[column].unique()]
    
    if diff == True:
        if column == 'Category':
            new_data = df.groupby(by=[column,date_var], as_index=False)[amount_var].sum()
            new_data[amount_var] = np.where(sorted(new_data[column].unique())==['Budget','Income'],new_data[amount_var] * -1,new_data[amount_var])
            new_data[amount_var] = np.where(new_data[column].isin(['Income','Expense']),new_data[amount_var]*-1,new_data[amount_var])
            new_data = new_data.groupby(by=date_var, as_index=False)[amount_var].sum()
        else:
            new_data = df.groupby(by=date_var, as_index=False)[amount_var].sum()
        graph_data = graph_data + [go.Scatter(name='Difference', mode='lines',
                                                        x = new_data['YearMonth'],
                                                        y = new_data['Amount'])]
            
    
    return dcc.Graph(figure={'data':graph_data})


def reset_datafiles():
    budget = file_read('datasets/budget.csv')
    spend = file_read('datasets/spend.csv')
    investment = file_read('datasets/investment.csv')

    budget['Date'] = pd.to_datetime(budget['Date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
    spend['Date'] = pd.to_datetime(spend['Date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
    spend['Date Applied'] = pd.to_datetime(spend['Date Applied'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
    investment['Date'] = pd.to_datetime(investment['Date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')

    budget.to_csv('datasets/budget.csv')
    spend.to_csv('datasets/spend.csv')
    investment.to_csv('datasets/investment.csv')