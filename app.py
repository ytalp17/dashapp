import dash
import os
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import numpy as np



app = dash.Dash(__name__)
server = app.server


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig

#Data Part
dir = os.path.dirname(__file__)
print(dir)
filename = os.path.join(dir, 'nba.xlsx')
filename2 = os.path.join(dir, 'newseason.csv')

nba = pd.read_excel(filename, header=[1])
new_season = pd.read_csv(filename2)

new_colnames = ['RANK', 'FULL NAME', 'TEAM', 'POS', 'AGE', 'GP', 'MPG','MIN','USG','TO','FTA','FT%','2PA','2P%','3PA','3P%',
               'efg', 'TS%', 'PPG' ,'RPG', 'TRB','APG','AST','SPG','BPG','TPG', 'VIV', 'ORT', 'DRT']

new_colnames2 = ['Unnamed', 'index', 'FULL NAME', 'POS', 'AGE', 'TEAM','G','GS', 'MPG','FG','FGA','FG%','3PM','3PA','3P%',
               '2P', '2PA', '2P%','eFG%','FT','FTA','FT%','ORB','DRB' ,'RPG','APG','SPG','BPG','TPG', 'PF','PPG']



nba.columns = new_colnames
nba['3PM']= nba['3PA']/nba['GP']*nba['3P%']
nba['FG%'] = (nba['2P%']*nba['2PA']+nba['3PA']*nba['3P%'])/(nba['2PA']+nba['3PA'])
nba = nba.round(2)

new_season.columns = new_colnames2
new_season = new_season[new_season['FULL NAME'].notna()]

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
player2 = ['Kris Dunn', 'Clint Capela']

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










# Define the app Layout
app.layout = html.Div(className='wrapper', children=[
                    #Header
                    html.Div(className='header', children=[html.H2('NBA FANTASY TEAM COMPARISON TOOL')]),
                    #Left-Col
                    html.Div(className='one', children=[
                        html.Div(className='dropdown_top1', children=[html.H3('''HOME TEAM: '''),
                        dcc.Dropdown(
                            id='player1',
                            options=players_options,
                            value=player1,
                            style={'backgroundColor': 'rgb(231,231,231)',
                                   'color': 'grey', 'font-family': 'sans-serif'},
                            multi=True),
                        dcc.Graph(id='hbar_graph', style={'margin-top': '80'}),
                        ]),

                    ]),
                    #Right-Col
                    html.Div(className='two', children=[

                            html.Div(className='dropdown_top2', children=[html.H3('''AWAY TEAM:'''),
                            dcc.Dropdown(
                                id='player2',
                                options=players_options,
                                value=player2,
                                multi=True,
                                style={'backgroundColor': 'rgb(231,231,231)',
                                        'color': 'grey', 'font-family': 'sans-serif'})
                            ]),

                            dcc.Graph(id='hbar_graph_right', style={'margin-top': '80'}),
                    ]),

                    #Center
                    html.Div(className='three', children=[
                    dbc.Card(
                    [
                        dcc.Graph(id='graph_example', style={'margin-top': '8vw'}),
                        dcc.RadioItems(
                            id='season',
                            options=[{'label': 'Season 2020-2021', 'value': 'nba'},
                                     {'label': 'Season 2021-2022', 'value': 'newseason'}],
                            value='nba',
                            labelStyle={'display': 'inline-block'},
                            )
                    ], style={"width": "35rem", "height": "30rem", "margin": "0 auto",'margin-bottom': '2.5vw'}),
                        #SolarGraph

                        #Upper Table for player 1
                        dbc.Row(id ='dash_table', children=[dashtable_1]),
                        dbc.Row(id ='dash_table_avg', children=[dashtable_1_avg]),
                        #Table for player 2
                        html.Div(className='table22', children=[
                            dbc.Row(id ='dash_table22_1', children=[dashtable_2]),
                            dbc.Row(id ='dash_table221_avg', children=[dashtable_2_avg])])
                        ])

            ])

@app.callback(

    Output('player1', 'options'),
    Input('season', 'value')
)

def set_options_player1(selected_data):
    if selected_data == 'nba':
        return [{'label': nba['FULL NAME'][i], 'value': nba['FULL NAME'][i]} for i in nba.index]
    else:
        return [{'label': new_season['FULL NAME'][i], 'value': new_season['FULL NAME'][i]} for i in new_season.index]

@app.callback(
    Output('player2', 'options'),

    Input('season', 'value')
)

def set_options_player2(selected_data):
    if selected_data == 'nba':

        return [{'label': nba['FULL NAME'][i], 'value': nba['FULL NAME'][i]} for i in
                nba.index]
    else:

        return [{'label': new_season['FULL NAME'][i], 'value': new_season['FULL NAME'][i]} for i in
                new_season.index]


@app.callback(
    [
    Output('table1', 'data'),
    Output('table1_avg', 'data'),
    Output('table2', 'data'),
    Output('table2_avg', 'data'),
    Output('graph_example', 'figure'),
    Output('hbar_graph', 'figure'),
    Output('hbar_graph_right', 'figure')
    ],

    [
    Input('player1', 'value'),
    Input('player2', 'value'),
    Input('season', 'value')
    ]
)

def tab_1_function(player1, player2,seas):

    x1 = nba[nba['FULL NAME'].isin(player1)]['GP'].values
    y1 = nba[nba['FULL NAME'].isin(player1)]['FULL NAME'].values

    x2 = nba[nba['FULL NAME'].isin(player2)]['GP'].values
    y2 = nba[nba['FULL NAME'].isin(player2)]['FULL NAME'].values


    fig1 = go.Figure(data=[go.Bar(
        x=x1,
        y=y1,
        orientation='h',
        marker_color='#45b3e7',
        opacity=1,
        )],
    )

    fig2 = go.Figure(data=[go.Bar(
        x=x2,
        y=y2,
        orientation='h',
        marker_color='#f0899c',
        opacity=1,
    )],
    )

    fig1.update_layout(
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.85],
        ),

        xaxis=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0, 0.90],
            range=[0,82],
        ),

        margin=dict(
            b=10,
            l=3,
            r=1,
            t=3),

        showlegend=False,
        height=230,
        width=300,
        plot_bgcolor='rgb(246,246,246)',

    )

    fig2.update_layout(
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.85], mirror='allticks', side='right', automargin=True,
        ),

        xaxis=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0.1, 1],
            autorange="reversed"
        ),

        margin=dict(
            b=10,
            l=1,
            r=3,
            t=3),

        showlegend=False,
        height=230,
        width=300,
        plot_bgcolor='rgb(246,246,246)',

    )
    fig1.add_vline(x=np.percentile(nba['GP'].values, 75), line_width=1, line_dash="dash", line_color="black")
    fig2.add_vline(x=np.percentile(nba['GP'].values, 75), line_width=1, line_dash="dash", line_color="black")


    if seas == 'nba':
        df1_for_plot = fantasy_stats(nba[nba['FULL NAME'].isin(player1)][avg_table_stats]).T.round(3)
        df1_for_plot.columns = ['score']
        df2_for_plot = fantasy_stats(nba[nba['FULL NAME'].isin(player2)][avg_table_stats]).T.round(3)
        df2_for_plot.columns = ['score']

        table_updated1 = nba[nba['FULL NAME'].isin(player1)].to_dict('records')
        table_updated1_avg = fantasy_stats(nba[nba['FULL NAME'].isin(player1)][avg_table_stats]).round(2).to_dict('records')
        table_updated2 = nba[nba['FULL NAME'].isin(player2)].to_dict('records')
        table_updated2_avg = fantasy_stats(nba[nba['FULL NAME'].isin(player2)][avg_table_stats]).round(2).to_dict('records')

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
                    showticklabels=False,
                    ticks='',
                    gridcolor='black'),
            ),
            showlegend=False,
            template="plotly_dark",
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font_color="black",
            font_size=15
        )

        return table_updated1, table_updated1_avg, table_updated2, table_updated2_avg, fig, fig1, fig2



    else:
        df1_for_plot = fantasy_stats(new_season[new_season['FULL NAME'].isin(player1)][avg_table_stats]).T.round(3)
        df1_for_plot.columns = ['score']
        df2_for_plot = fantasy_stats(new_season[new_season['FULL NAME'].isin(player2)][avg_table_stats]).T.round(3)
        df2_for_plot.columns = ['score']

        table_updated1 = new_season[new_season['FULL NAME'].isin(player1)].to_dict('records')
        table_updated1_avg = fantasy_stats(new_season[new_season['FULL NAME'].isin(player1)][avg_table_stats]).round(2).to_dict(
            'records')
        table_updated2 = new_season[new_season['FULL NAME'].isin(player2)].to_dict('records')
        table_updated2_avg = fantasy_stats(new_season[new_season['FULL NAME'].isin(player2)][avg_table_stats]).round(2).to_dict(
            'records')



        list_scores = [df1_for_plot.index[i].capitalize() + ' = ' + str(df1_for_plot['score'][i]) for i in range(len(df1_for_plot))]

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
        margin=dict(l=20, r=20, t=20, b=80),
        showlegend=False,
        template="plotly_dark",
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color="black",
        font_size=15
        )


    return table_updated1, table_updated1_avg, table_updated2, table_updated2_avg, fig, fig1, fig2


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)