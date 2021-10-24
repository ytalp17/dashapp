import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table



app = dash.Dash(__name__)
server = app.server


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig

#Data Part
nba = pd.read_excel('/Users/yigitalp/PycharmProjects/nba/nba.xlsx',header=[1])

new_colnames = ['RANK', 'FULL NAME', 'TEAM', 'POS', 'AGE', 'GP', 'MPG','MIN','USG','TO','FTA','FT%','2PA','2P%','3PA','3P%',
               'efg', 'TS%', 'PPG' ,'RPG', 'TRB','APG','AST','SPG','BPG','TPG', 'VIV', 'ORT', 'DRT']
nba.columns = new_colnames
nba['3PM']= nba['3PA']/nba['GP']*nba['3P%']
nba['FG%'] = (nba['2P%']*nba['2PA']+nba['3PA']*nba['3P%'])/(nba['2PA']+nba['3PA'])
nba = nba.round(2)

fantasy_skills = ['FT%','3PM','PPG','RPG','APG','SPG','BPG','TPG','FG%']
table_stats = ['FULL NAME', 'TEAM', 'POS', 'MPG','FT%','3PM','PPG','RPG','APG','SPG','BPG','TPG','FG%']
avg_table_stats = ['FT%','3PM','PPG','RPG','APG','SPG','BPG','TPG','FG%']


def fantasy_stats(df):
    final = []


    for i in df.columns:
        if i in [col for col in df.columns if '%' in col]:
            final.append(df[i].mean())
        else:
            final.append(df[i].sum())

    f_df = pd.DataFrame(final).T
    f_df.columns = df.columns
    return f_df


player1 = ['Kevin Durant', 'Mike James']
player2 = ['Russell Westbrook', 'Clint Capela']

#Interactive Component
players_options = []
for i in nba.index:
    players_options.append({'label': nba['FULL NAME'][i], 'value': nba['FULL NAME'][i]})


dashtable_1 = dash_table.DataTable(
    id='table1',
    columns=[{"name": i, "id": i} for i in nba[table_stats]],
    data=nba[nba['FULL NAME'].isin(player1)].to_dict('records'),
    style_as_list_view=True,
    style_header={'backgroundColor': 'rgb(231,231,231)', 'color':'black'},
    style_data={
        'backgroundColor': 'white',
        'color': 'black'
    }
)

dashtable_1_avg = dash_table.DataTable(
    id='table1_avg',
    columns=[{"name": i, "id": i} for i in nba[avg_table_stats]],
    data=fantasy_stats(nba[nba['FULL NAME'].isin(player1)][avg_table_stats]).to_dict('records'),
    style_as_list_view=True,
    style_data={
        'backgroundColor': 'white',
        'color': 'black'
    }
)

dashtable_2 = dash_table.DataTable(
    id='table2',
    columns=[{"name": i, "id": i} for i in nba[table_stats]],
    data=nba[nba['FULL NAME'].isin(player2)].to_dict('records'),
    style_as_list_view=True,
    style_header={'backgroundColor': 'rgb(231,231,231)', 'color':'black'},
    style_data={
        'backgroundColor': 'white',
        'color': 'black'
    },
)

dashtable_2_avg = dash_table.DataTable(
    id='table2_avg',
    columns=[{"name": i, "id": i} for i in nba[avg_table_stats]],
    data=fantasy_stats(nba[nba['FULL NAME'].isin(player2)][avg_table_stats]).to_dict('records'),
    style_as_list_view=True,
    style_data={
        'backgroundColor': 'white',
        'color': 'black'
    },
)


#Components
options = [{'label': 'FT%', 'value': 'FT%'},
           {'label': '3P%', 'value': '3P%'},
           {'label': 'PPG', 'value': 'PPG'},
           {'label': 'RPG', 'value': 'RPG'},
           {'label': 'APG', 'value': 'APG'},
           {'label': 'SPG', 'value': 'SPG'},
           {'label': 'BPG', 'value': 'BPG'},
           {'label': 'TOPG', 'value': 'TOPG'},
           {'label': 'TS', 'value': 'TS'}]

#html.Div(className='header_par', children=[html.H2('NBA PLAYER COMPARISON'),
#html.P('''Visualising time series with Plotly - Dash''')],style={'padding-bottom': 20}),

                                           # Define the app
app.layout = html.Div(className='wrapper', children=[html.Div(className='header',children=[html.H2('NBA FANTASY TEAM COMPARISON TOOL')]),                html.Div(className='one', children=[
                    html.Div(className='dropdown_top1', children=[html.H3('''Build up Team 1: '''), dcc.Dropdown(
                        id='player1',
                        options=players_options,
                        value=player1,
                        style={'backgroundColor': 'rgb(231,231,231)',
                               'color': 'grey','font-family': 'sans-serif'},
                        multi=True), html.P('''Visualising time series with Plotly - Dash''')], style={'padding-bottom': 10})]),
                html.Div(className='two', children=[
                    html.Div(className='dropdown_top2', children=[html.H3('''Build up Team 2:'''), dcc.Dropdown(
                        id='player2',
                        options=players_options,
                        value=player2,
                        multi=True,
                        style={'backgroundColor': 'rgb(231,231,231)',
                               'color': 'grey','font-family': 'sans-serif'})])
                       ]),
                html.Div(className='three', children=[

                    dcc.Graph(id='graph_example', style={'width': '18%', 'margin-left': '9vw','margin-top': '5vw'}),
                    dbc.Row(id ='dash_table', children=[dashtable_1]),
                    dbc.Row(id ='dash_table_avg', children=[dashtable_1_avg]),
                    html.Div(className='table22', children=[dbc.Row(id ='dash_table22_1', children=[dashtable_2]),
                    dbc.Row(id ='dash_table221_avg', children=[dashtable_2_avg])])])

])


@app.callback(
    [
    Output('graph_example', 'figure'),
    Output('table1', 'data'),
    Output('table1_avg', 'data'),
    Output('table2', 'data'),
    Output('table2_avg', 'data')

    ],

    [
    Input('player1', 'value'),
    Input('player2', 'value')

    ]
)

def tab_1_function(player1, player2):
    # scatterpolar
    df1_for_plot = fantasy_stats(nba[nba['FULL NAME'].isin(player1)][avg_table_stats]).T.round(3)
    df1_for_plot.columns = ['score']
    df2_for_plot = fantasy_stats(nba[nba['FULL NAME'].isin(player2)][avg_table_stats]).T.round(3)
    df2_for_plot.columns = ['score']
    list_scores = [df1_for_plot.index[i].capitalize() + ' = ' + str(df1_for_plot['score'][i]) for i in
                   range(len(df1_for_plot))]
    text_scores_1 = 'Team 1'
    for i in list_scores:
        text_scores_1 += '<br>' + i

    list_scores = [df2_for_plot.index[i].capitalize() + ' = ' + str(df2_for_plot['score'][i]) for i in
                   range(len(df2_for_plot))]
    text_scores_2 = 'Team 2 '
    for i in list_scores:
        text_scores_2 += '<br>' + i

    fig = go.Figure(data=go.Scatterpolar(
        r=df1_for_plot['score'],
        theta=df1_for_plot.index,
        fill='toself',
        marker_color='#45b3e7',
        opacity=1,
        hoverinfo="text",
        name=text_scores_1,
        text=[df1_for_plot.index[i] + ' = ' + str(df1_for_plot['score'][i]) for i in range(len(df1_for_plot))]
    ))
    fig.add_trace(go.Scatterpolar(
        r=df2_for_plot['score'],
        theta=df2_for_plot.index,
        fill='toself',
        marker_color='#f0899c',
        hoverinfo="text",
        name=text_scores_2,
        text=[df2_for_plot.index[i] + ' = ' + str(df2_for_plot['score'][i]) for i in range(len(df2_for_plot))]
    ))

    fig.update_layout(
        polar=dict(
            hole=0.1,
            bgcolor='rgb(246,246,246)',
            radialaxis=dict(
                visible=True,
                type='linear',
                autotypenumbers='strict',
                autorange=True,
                range=[0, 500],
                angle=90,
                showline=False,
                showticklabels=False, ticks='',
                gridcolor='black'),
        ),
        width=420,
        height=420,
        margin=dict(l=80, r=80, t=20, b=20),
        showlegend=False,
        template="plotly_dark",
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color="black",
        font_size=15
    )
    # table 1
    table_updated1 = nba[nba['FULL NAME'].isin(player1)].to_dict('records')
    table_updated1_avg = fantasy_stats(nba[nba['FULL NAME'].isin(player1)][avg_table_stats]).round(2).to_dict('records')

    # table 2
    table_updated2 = nba[nba['FULL NAME'].isin(player2)].to_dict('records')
    table_updated2_avg = fantasy_stats(nba[nba['FULL NAME'].isin(player2)][avg_table_stats]).round(2).to_dict('records')



    return fig, table_updated1, table_updated1_avg, table_updated2, table_updated2_avg


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)