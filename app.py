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
import re
import pickle
import xlrd




#meta_tags are for responsive layout


app = dash.Dash(__name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    )
server = app.server

app.css.append_css({"external_url": "./assets/style.css"})


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig

#Data Part

dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'PlayerRankings2021_pergame_all.csv')
filename2 = os.path.join(dir, 'BBM_PlayerRankings.xls')
pickle_file = os.path.join(dir, 'nba_population_stat.pickle')

nba = pd.read_csv(filename)
new_season = pd.read_excel(filename2)

z_stats = ['p/g', '3/g', 'r/g', 'a/g', 's/g', 'b/g', 'to/g', 'ft%', 'fg%', 'fta/g', 'fga/g']

features_of_interest = ['Name', 'Team', 'Pos', 'g', 'm/g', 'p/g', '3/g', 'r/g', 'a/g',
                        's/g', 'b/g', 'fg%', 'fga/g', 'ft%', 'fta/g', 'to/g']

df = new_season[z_stats]
new_season = new_season[features_of_interest]

##Z-stats
#pre-determined population stat based on the last season

with open(pickle_file, 'rb') as handle:
    pop_stats = pickle.load(handle)

#define new random variable called ft fg impact its like weighted by volume
df['FT%!'] = (df['ft%']-pop_stats['sample_mean']['ft%'])*df['fta/g']
df['FG%!'] = (df['fg%']-pop_stats['sample_mean']['fg%'])*df['fga/g']

#add newly created summary statistics to the main dictionary (population dict)
pop_stats['sample_mean']['ft_imp'] = df['FT%!'].mean()
pop_stats['sample_mean']['fg_imp'] = df['FG%!'].mean()
pop_stats['sample_std']['ft_imp'] = df['FT%!'].std()
pop_stats['sample_std']['fg_imp'] = df['FG%!'].std()

#calcualte Z score for each statistics for each active player
df['3PM_z'] = (df['3/g']-pop_stats['sample_mean']['3/g'])/pop_stats['sample_std']['3/g']
df['PPG_z'] = (df['p/g']-pop_stats['sample_mean']['p/g'])/pop_stats['sample_std']['p/g']
df['RPG_z'] = (df['r/g']-pop_stats['sample_mean']['r/g'])/pop_stats['sample_std']['r/g']
df['APG_z'] = (df['a/g']-pop_stats['sample_mean']['a/g'])/pop_stats['sample_std']['a/g']
df['SPG_z'] = (df['s/g']-pop_stats['sample_mean']['s/g'])/pop_stats['sample_std']['s/g']
df['BPG_z'] = (df['b/g']-pop_stats['sample_mean']['b/g'])/pop_stats['sample_std']['b/g']
df['TPG_z'] = (df['to/g']-pop_stats['sample_mean']['to/g'])/pop_stats['sample_std']['to/g']
df['FT%_z'] = (df['FT%!']-pop_stats['sample_mean']['ft_imp'])/pop_stats['sample_std']['ft_imp']
df['FG%_z'] = (df['FG%!']-pop_stats['sample_mean']['fg_imp'])/pop_stats['sample_std']['fg_imp']

#Negative turnover
df['TPG_z'] = -df['TPG_z']

#sum them up for ranking (sort of)
z_s = ['FT%_z', '3PM_z', 'PPG_z', 'RPG_z', 'APG_z', 'SPG_z', 'BPG_z', 'TPG_z', 'FG%_z']
df['z_Total'] = df[z_s].sum(axis=1)

#add names to the created z_scores data set
name = pd.DataFrame(new_season['Name'])
z_scores = pd.concat([name, df], axis=1)
z_scores = z_scores.reset_index(drop=True)


final_column = ['Name', 'FT%_z', '3PM_z', 'PPG_z', 'RPG_z', 'APG_z', 'SPG_z',
                'BPG_z', 'TPG_z', 'FG%_z', 'z_Total']

z_scores = z_scores[final_column]
new_season = pd.merge(new_season, z_scores, on="Name")


new_colnames = ['NAME', 'TEAM', 'POS', 'GP', 'MPG', 'PPG', '3PG', 'RPG', 'APG',
                'SPG', 'BPG', 'FG%', 'FGA', 'FT%', 'FTA', 'TPG', 'FTz', '3PGz', 'PPGz',
                'RPGz', 'APGz', 'SPGz', 'BPGz', 'TPGz', 'FGz', 'TOTALz']

new_season.columns = new_colnames
nba = nba.drop(['FT%!', 'FG%!'], axis=1)
nba.columns = new_colnames


fantasy_skills = ['FT%', '3PG', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'TPG', 'FG%']

table_stats = ['NAME', 'TEAM', 'POS', 'GP', 'MPG', 'PPG', '3PG', 'RPG', 'APG',
               'SPG', 'BPG', 'FG%', 'FGA', 'FT%', 'FTA', 'TPG', 'FTz', '3PGz', 'PPGz',
               'RPGz', 'APGz', 'SPGz', 'BPGz', 'TPGz', 'FGz', 'TOTALz']

nba = nba.round(2)
new_season = new_season.round(2)
player_names_list = new_season['NAME'].tolist()




#aggregated comparison stats
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

#place holders
player1 = ['Kevin Durant']
player2 = ['Kris Dunn']


###Interactive Component

#player pool (drop down options)
players_options = []
for i in nba.index:
    players_options.append({'label': nba['NAME'][i], 'value': nba['NAME'][i]})  #update here!

#color_code
z = ['FTz', '3PGz', 'PPGz', 'RPGz', 'APGz', 'SPGz', 'BPGz', 'TPGz', 'FGz']
df_numeric = new_season[z]
min = new_season[z].min().min()
max = new_season[z].max().max()
colors = ['#44000D', '#83142C', '#AD1D45', '#F9D276', '#F9D276', '#3A9188', '#044A42', '#062925']
ranges = [min, -3, -2, -1, 0, 1, 2, 3, max]

styles = []
legend = []

for i in range(1, len(ranges)):
    min_bound = ranges[i - 1]
    max_bound = ranges[i]
    backgroundColor = colors[i - 1]
    color = 'white'

    for column in df_numeric.columns:
        styles.append({
            'if': {
                'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(ranges) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'backgroundColor': backgroundColor,
            'color': color
        })

    if ((min_bound == -3) | (min_bound == -2) | (min_bound == -1)):
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '20px'}, children=[
                html.Div(
                    style={
                    'backgroundColor': backgroundColor,
                    'borderLeft': '1px rgb(50, 50, 50) solid',
                    'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )
    elif ((min_bound == 0) | (min_bound == 1) | (min_bound == 2)):
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '20px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound+1, 2), style={'paddingLeft': '2px'})
            ])
        )
    else:
        continue

#Table1
dashtable_1 = dash_table.DataTable(
    id='table1',
    style_as_list_view=True,
    columns=[{"name": i, "id": i} for i in nba[table_stats]],
    data=nba[nba['NAME'].isin(player1)].to_dict('records'),
    style_header={'backgroundColor': 'rgb(36,38,50)',
                  'color': 'white'},
    style_data={
        'backgroundColor': 'rgb(36,38,50)',
        'color': 'white'},

    style_cell={'textAlign': 'center', 'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                'whiteSpace': 'normal'},
    style_table={'overflowX': 'scroll'},
    style_data_conditional=styles,
    fixed_columns={'headers': True, 'data': 1},

)


#Table1 results (avg)_part
dashtable_1_avg = dash_table.DataTable(
    id='table1_avg',
    columns=[{"name": i, "id": i} for i in nba[fantasy_skills]], #update
    data=fantasy_stats(nba[nba['NAME'].isin(player1)][fantasy_skills]).to_dict('records'), #update
    style_as_list_view=True,
    style_header={'backgroundColor': 'rgb(36,38,50)',
                  'color': 'white'},
    style_data={
        'backgroundColor': 'rgb(36,38,50)',
        'color': 'white'},

    style_cell={'textAlign': 'center', 'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                'whiteSpace': 'normal'},
    style_table={'overflowX': 'scroll'},

)

#Table2
dashtable_2 = dash_table.DataTable(
    id='table2',
    style_as_list_view=True,

    columns=[{"name": i, "id": i} for i in nba[table_stats]], #update
    data=nba[nba['NAME'].isin(player2)].to_dict('records'), #update
    style_header={'backgroundColor': 'rgb(36,38,50)',
                  'color': 'white'},
    style_data={
        'backgroundColor': 'rgb(36,38,50)',
        'color': 'white'
    },
    style_cell={'textAlign': 'center', 'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                'whiteSpace': 'normal'},
    style_table={'overflowX': 'scroll'},
    style_data_conditional=styles,
    fixed_columns={'headers': True, 'data': 1},

)

#Table2 avg results
dashtable_2_avg = dash_table.DataTable(
    id='table2_avg',
    columns=[{"name": i, "id": i} for i in nba[fantasy_skills]], #update
    data=fantasy_stats(nba[nba['NAME'].isin(player2)][fantasy_skills]).to_dict('records'), #update
    style_as_list_view=True,
    style_header={'backgroundColor': 'rgb(36,38,50)',
                  'color': 'white'},
    style_data={
        'backgroundColor': 'rgb(36,38,50)',
        'color': 'white'
    },
    style_cell={'textAlign': 'center', 'minWidth': '60px', 'width': '60px', 'maxWidth': '60px',
                'whiteSpace': 'normal'},
    style_table={'overflowX': 'scroll'},

)


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Yahoo! Fantasy Basketball"),
                    html.H6("Team/Player Comparison Tool"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="ABOUT", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("basketball.png"))

                    ),
                ],
            ),
        ]
    )


def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        ###### What is this app about?
                        This is a dashboard for monitoring real-time process quality along manufacture production line.
                        ###### What does this app shows
                        Click on buttons in `Parameter` column to visualize details of measurement trendlines on the bottom panel.
                        The sparkline on top panel and control chart on bottom panel show Shewhart process monitor using mock data.
                        The trend is updated every other second to simulate real-time measurements. Data falling outside of six-sigma control limit are signals indicating 'Out of Control(OOC)', and will
                        trigger alerts instantly for a detailed checkup.

                        Operators may stop measurement by clicking on `Stop` button, and edit specification parameters by clicking specification tab.
                        ###### Source Code
                        You can find the source code of this app on our [Github repository](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-manufacture-spc-dashboard).
                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )

val = 'Christian Wood Desmond Bane Derrick White Steven Adams Julius Randle'

#Define the app Layout (html part)
app.layout = html.Div(id='big-app-container', children=[
                    build_banner(),
                    html.Div(className='wrapper', children=[
                        html.Div(className='left', children=[
                            html.Div(className='dropdown_top1', children=[
                                html.H5('''HOME TEAM: '''),
                                dcc.Dropdown(
                                    id='player1',
                                    options=players_options,
                                    value=player1,
                                    style={'autosize': True},
                                    multi=True),
                                    dcc.Graph(id='hbar_graph', style={'background-color': 'rgb(22,26,39)',
                                                                      'autosize': True}),
                            ]),
                                    html.Div(className='left2', children=[
                                    dcc.Input(id="roster1",
                                              placeholder='Paste Your Yahoo Roster Here',
                                              type='text',
                                              value=val,

                                          ),]),

                        ]),

                        html.Div(className='center', children=[
                            dcc.Graph(id='graph_example', style={
                                                                'autosize': True},
                                      ),
                            html.Div(className='radio', children=[
                            dcc.RadioItems(
                                            id='season',
                                            options=[{'label': 'Season 2020-2021',
                                                      'value': 'nba'},
                                                     {'label': 'Season 2021-2022',
                                                      'value': 'newseason'}],
                                            value='nba',
                                            labelStyle={'display': 'inline-block'},
                            ), ]),
                            html.Div(className='legend', children=[
                                html.Small('*The table is scrollable through right!'),
                                html.Div(legend)
                            ]),
                            html.Div(className='table11', children=[
                                dbc.Row(id ='dash_table', children=[dashtable_1]),
                                dbc.Row(id ='dash_table_avg', children=[dashtable_1_avg]),
                            ]),

                            html.Div(className='table22', children=[
                                dbc.Row(id ='dash_table22_1', children=[dashtable_2]),
                                dbc.Row(id ='dash_table221_avg', children=[dashtable_2_avg])
                            ]),
                        ]),

                        html.Div(className='right', children=[
                            html.Div(className='dropdown_top2', children=[html.H5('''AWAY TEAM:'''),
                                dcc.Dropdown(
                                              id='player2',
                                              options=players_options,
                                              value=player2,
                                              multi=True,
                                              style={'autosize': True})
                            ]),
                                dcc.Graph(id='hbar_graph_right',
                                          style={
                                                 'autosize': True
                                                },
                                ),
                                html.Div(className='right2', children=[
                                    dcc.Input(id="roster2",
                                              placeholder='Paste Your Yahoo Roster Here',
                                              type='text',
                                              value='',)
                                          ]),

                        ]),
                    ]), generate_modal(),
              ])



#Call-backs section

# ======= Callbacks for modal popup ======= check later?
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}


#Paste roster to input (left)
@app.callback(
    Output("player1", "value"),
    Input("roster1", "value"),
)

#parse "pasted text" and find the ones that match with the NAMEs in the pool (player_names_list)
def auto_fill1(roster1):
    my_players_raw = [re.findall(str(player), roster1) for player in player_names_list]
    my_players = [emp for emp in my_players_raw if emp != []]
    my_players_flat = [item for sublist in my_players for item in sublist]
    return my_players_flat

#Paste roster to input (right)
@app.callback(
    Output("player2", "value"),
    Input("roster2", "value"),
)
def auto_fill1(roster2):
    my_players_raw = [re.findall(str(player), roster2) for player in player_names_list]
    my_players = [emp for emp in my_players_raw if emp != []]
    my_players_flat = [item for sublist in my_players for item in sublist]
    return my_players_flat



#Arrange Season 2021-2022 (current) or 2020-2021
@app.callback(

    [Output('player1', 'options'), Output('player2', 'options')],
    Input('season', 'value'),
)

def set_options_player1(selected_data):
    if selected_data == 'nba':
        player_pool1 = [{'label': nba['NAME'][i], 'value': nba['NAME'][i]} for i in nba.index] #update
        return player_pool1, player_pool1
    else:
        player_pool2 = [{'label': new_season['NAME'][i], 'value': new_season['NAME'][i]} for i in new_season.index]#update

        return player_pool2, player_pool2



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

def tab_1_function(player1, player2, seas): #seas =season
    #left
    x1 = nba[nba['NAME'].isin(player1)]['GP'].values
    y1 = nba[nba['NAME'].isin(player1)]['NAME'].values

    #right
    x2 = nba[nba['NAME'].isin(player2)]['GP'].values
    y2 = nba[nba['NAME'].isin(player2)]['NAME'].values

    #left horizontal bar for game played
    fig1 = go.Figure(
        data=[go.Bar(
        x=x1,
        y=y1,
        orientation='h',
        marker_color='rgb(245,211,100)',
        opacity=1,
        showlegend=True,
        )],
    )
    # right horizontal bar for game played
    fig2 = go.Figure(
        data=[go.Bar(
        x=x2,
        y=y2,
        orientation='h',
        marker_color='rgb(250,78,97)',
        opacity=1,
        showlegend=True,
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
            zeroline=True,
            showline=False,
            showgrid=False,
            showticklabels=True,
            domain=[0, 0.90],
            range=[0, 82],
            title="Game Played-Previous Season",
            titlefont={"color": "white"},
        ),
        margin=dict(
            b=10,
            l=3,
            r=1,
            t=3),
        showlegend=False,
        #height=230,
        #width=300,
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
    )

    fig1.layout.plot_bgcolor = 'rgb(22,26,39)'
    fig1.layout.paper_bgcolor = 'rgb(22,26,39)'

    fig2.update_layout(
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.85], mirror='allticks', side='right', automargin=True,
        ),
        xaxis=dict(
            zeroline=True,
            showline=False,
            showticklabels=True,
            showgrid=False,
            domain=[0.1, 1],
            autorange="reversed",
            title="Game Played-Previous Season",
            titlefont={"color": "white"},
        ),
        margin=dict(
            b=10,
            l=1,
            r=3,
            t=3),
        showlegend=False,
        #height=230,
        #width=300,
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
    )
    fig2.layout.plot_bgcolor = 'rgb(22,26,39)'
    fig2.layout.paper_bgcolor = 'rgb(22,26,39)'


    fig1.add_vline(x=np.percentile(nba['GP'].values, 75), line_width=2, line_dash="dash", line_color="white") #update
    fig2.add_vline(x=np.percentile(nba['GP'].values, 75), line_width=2, line_dash="dash", line_color="white") #update

    if seas == 'nba':
        df1_for_plot = fantasy_stats(nba[nba['NAME'].isin(player1)][fantasy_skills]).T.round(3)
        df1_for_plot.columns = ['score']
        df2_for_plot = fantasy_stats(nba[nba['NAME'].isin(player2)][fantasy_skills]).T.round(3)
        df2_for_plot.columns = ['score']

        table_updated1 = nba[nba['NAME'].isin(player1)].to_dict('records')
        table_updated1_avg = fantasy_stats(nba[nba['NAME'].isin(player1)][fantasy_skills]).round(2).to_dict('records')
        table_updated2 = nba[nba['NAME'].isin(player2)].to_dict('records')
        table_updated2_avg = fantasy_stats(nba[nba['NAME'].isin(player2)][fantasy_skills]).round(2).to_dict('records')

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
            marker_color='rgb(245,211,100)',
            opacity=1,
            hoverinfo="text",
            name=text_scores_1,
            text=[df1_for_plot.index[i] + ' = ' + str(df1_for_plot['score'][i]) for i in range(len(df1_for_plot))]
        ))
        fig.add_trace(go.Scatterpolar(
            r=df2_for_plot['score'],
            theta=df2_for_plot.index,
            fill='toself',
            marker_color='rgb(250,78,97)',
            hoverinfo="text",
            name=text_scores_2,
            text=[df2_for_plot.index[i] + ' = ' + str(df2_for_plot['score'][i]) for i in range(len(df2_for_plot))]
        ))

        fig.update_layout(
            polar=dict(
                hole=0.1,
                bgcolor='rgb(9,65,69)',
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
                    gridcolor='rgb(40,132,117)'),
            ),
            showlegend=False,
            template="plotly_dark",
            plot_bgcolor='rgb(22,26,39)',
            paper_bgcolor='rgb(22,26,39)',
            font_color='white',
            font_size=14
        )

        return table_updated1, table_updated1_avg, table_updated2, table_updated2_avg, fig, fig1, fig2



    else:
        df1_for_plot = fantasy_stats(new_season[new_season['NAME'].isin(player1)][fantasy_skills]).T.round(3)
        df1_for_plot.columns = ['score']
        df2_for_plot = fantasy_stats(new_season[new_season['NAME'].isin(player2)][fantasy_skills]).T.round(3)
        df2_for_plot.columns = ['score']

        table_updated1 = new_season[new_season['NAME'].isin(player1)].to_dict('records')
        table_updated1_avg = fantasy_stats(new_season[new_season['NAME'].isin(player1)][fantasy_skills]).round(2).to_dict(
            'records')
        table_updated2 = new_season[new_season['NAME'].isin(player2)].to_dict('records')
        table_updated2_avg = fantasy_stats(new_season[new_season['NAME'].isin(player2)][fantasy_skills]).round(2).to_dict(
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
            marker_color='rgb(245,211,100)',
            opacity=1,
            hoverinfo="text",
            name=text_scores_1,
            text=[df1_for_plot.index[i] + ' = ' + str(df1_for_plot['score'][i]) for i in range(len(df1_for_plot))]
        ))

        fig.add_trace(go.Scatterpolar(
            r=df2_for_plot['score'],
            theta=df2_for_plot.index,
            fill='toself',
            marker_color='rgb(250,78,97)',
            hoverinfo="text",
            name=text_scores_2,
            text=[df2_for_plot.index[i] + ' = ' + str(df2_for_plot['score'][i]) for i in range(len(df2_for_plot))]
        ))

        fig.update_layout(
            polar=dict(
                hole=0.1,
                bgcolor='rgb(9,65,69)',
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
                    gridcolor='rgb(40,132,117)'),
            ),
            showlegend=False,
            template="plotly_dark",
            plot_bgcolor='rgb(22,26,39)',
            paper_bgcolor='rgb(22,26,39)',
            font_color='white',
            font_size=14
        )


    return table_updated1, table_updated1_avg, table_updated2, table_updated2_avg, fig, fig1, fig2


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)