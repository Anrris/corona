import wget
import pandas as pd
import os
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objects as go
import plotly


class CoronaPlots(object):
    filename = wget.download(
        'https://raw.githubusercontent.com/'
        'CSSEGISandData/COVID-19/master/csse_covid_19_data/'
        'csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
    )
    df1 = pd.read_csv(filename)
    os.remove(filename)
    
    filename = wget.download(
        'https://raw.githubusercontent.com/'
        'COVID19Tracking/covid-tracking-data/master/data/states_daily_4pm_et.csv'
    )
    df2 = pd.read_csv(filename)
    os.remove(filename)
    
    hex_colors = [
        '#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2',
        '#7f7f7f','#bcbd22','#17becf','#7f0000','#000000','#04ab08','#0000fb',
    ]
    
    @classmethod
    def plot_global_cases(cls, auto_open = False):
        dfAll = cls.df1
        dfSub = dfAll[dfAll['Province/State'].isna()]
        dfSub = dfSub.drop(columns=['Province/State', 'Lat', 'Long'])
        dfSub = dfSub.T
        dfSub.columns = dfSub.iloc[0]
        dfSub = dfSub.drop(['Country/Region'])
        
        country_with_state = dfAll[~dfAll['Province/State'].isna()]['Country/Region'].unique()
        
        for country in country_with_state:
            df = dfAll[dfAll['Country/Region']==country]
            df = df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
            row_total = None
            for _, row in df.iterrows():
                for i, r in enumerate(row):
                    if pd.isna(r):
                        row[i] = 0

                if row_total is None:
                    row_total = row
                    continue
                row_total = row_total + row
            dfSub.insert(0, country, list(row_total), True)
        
        dfSub = dfSub.rename(columns={"Country/Region": "date"})
        last_date = dfSub.index[-1]
        count_names = []
        for count, name in zip(list(dfSub.loc[last_date]), list(dfSub.columns)):
            if type(count) is str:
                continue
            count_names.append((count, name))
            
        count_names.sort(key = lambda x: x[0], reverse=True)
        
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.05)
        for _, country in count_names:
            date = list(dfSub.index)
            count = list(dfSub[country])
            last_count = count[-1]
            while(pd.isna(last_count)):
                count = count[:-1]
                last_count = count[-1]
            color = cls.hex_colors[int(last_count) % len(cls.hex_colors)]
        
            fig.add_trace(
                go.Scatter(
                    x=date, y=count, mode='lines+markers', name=f'{country} accumulated: last day = {last_count}',
                    legendgroup=country, line=dict(color=color), marker=dict(color=color),
                    hoverinfo='text',
                    hovertext=[f'{country}, {t}={c}' for t, c in zip(dfSub.index, dfSub[country])]
                ),
                row=1, col=1
            )
            
            count = list(dfSub[country])
            count_diff = np.array(count) - np.array([0]+count[:-1])
            fig.add_trace(
                go.Scatter(
                    x=date, y=count_diff , mode='lines+markers', name=f'{country} daily',
                    legendgroup=country, line=dict(color=color), marker=dict(color=color), hoverinfo='text',
                    hovertext=[f'{country}, {t}, daily new case={c}' for t, c in zip(date, count_diff)]
                ),
                row=2, col=1
            )
            
        fig.update_layout( title="Corona virus growth: Global")
        fig.update_yaxes(title_text="Accumulative count", row=1, col=1)
        fig.update_yaxes(title_text="Daily count", row=2, col=1)
        
        plotly.offline.plot(fig, filename = 'corona_global.html', auto_open=auto_open)
        return fig
    
    @classmethod
    def plot_usa_cases(cls, auto_open=False):
        df = cls.df1
        dfUS = df[df['Country/Region']=='US']
        
        dfUS = dfUS.T
        dfUS.columns = dfUS.iloc[0]
        dfUS = dfUS.drop(['Country/Region', 'Lat', 'Long', 'Province/State'])
        last_date = dfUS.index[-1]
        
        count_names = []
        for count, name in zip(list(dfUS.loc[last_date]), list(dfUS.columns)):
            if type(count) is str:
                continue
            count_names.append((count, name))
        count_names.sort(key = lambda x: x[0], reverse=True)
        
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1)
        for _, name in count_names:

            date = list(dfUS.index)
            count = list(dfUS[name])
            last_count = count[-1]
            while(pd.isna(last_count)):
                count = count[:-1]
                last_count = count[-1]
            color = cls.hex_colors[int(last_count) % len(cls.hex_colors)]
            date = date[30:]
            count = count[30:]
            fig.add_trace(
                go.Scatter(
                    x=date, y=count, mode='lines+markers', name=f'{name} accumulated: last day = {count[-1]}', legendgroup=name,
                    line=dict(color=color), marker=dict(color=color),
                    hoverinfo='text',
                    hovertext=[f'{name}, {t}={c}' for t, c in zip(date, count)]
                ),
                row=1, col=1
            )
            
            count = list(count)
            count_diff = np.array(count) - np.array([0]+count[:-1])
            fig.add_trace(
                go.Scatter(
                    x=date, y=count_diff, mode='lines+markers', name=f'{name} daily new case: last day = {count_diff[-1]}', legendgroup=name,
                    line=dict(color=color), marker=dict(color=color),
                    hoverinfo='text',
                    hovertext=[f'{name}, {t}={c}' for t, c in zip(date, count_diff)]
                ),
                row=2, col=1
            )
        
        fig.update_layout(title="Corona virus tracking: USA positive cases by states")
        fig.update_yaxes(title_text="Accumulative count", row=1, col=1)
        fig.update_yaxes(title_text="Daily count", row=2, col=1)
        
        plotly.offline.plot(fig, filename = 'corona_us.html', auto_open=auto_open)
        return fig
    
    @classmethod
    def plot_usa_pos_neg_tracking(cls, auto_open=False):
        df = cls.df2
        states = df.state.unique()
        
        total_cols = 5
        total_rows = int(len(states)/total_cols) + 1
        
        fig = make_subplots(rows=total_rows, cols=total_cols, subplot_titles=states)
        for idx, state in enumerate(states):
            dfstate = df[df.state == state]
            dfstate = dfstate.sort_values(by='date')
            
            dates, positives, negatives = [],[],[]
            for idx, row in dfstate.iterrows():
                date, positive, negative = str(row.date), row.positive, row.negative
                if str(positive) == 'nan':
                    positive = 0
                if str(negative)=='nan':
                    negative = 0
                dates.append(pd.Timestamp(date))
                positives.append(positive)
                negatives.append(negative)
            data=[
                go.Bar(x=dates, y=positives, hovertext=['pos:'+str(int(p)) for p in positives]),
                go.Bar(x=dates, y=negatives, hovertext=['neg:'+str(int(n)) for n in negatives])
            ]
            
            cols = total_cols
            i, j = int(idx/cols)+1, idx%cols+1
            fig.add_trace(data[0], row=i, col=j)
            fig.add_trace(data[1], row=i, col=j)
            
        fig.update_layout(title="Corona virus tracking: USA positive & negative cases by states")
        fig.update_layout(barmode='stack', height=2000, showlegend=False)
        plotly.offline.plot(fig, filename = 'corona_states.html', auto_open=auto_open)
        return fig
