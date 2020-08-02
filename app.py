import os
import pathlib
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_daq as daq
from wordcloud import WordCloud
from io import BytesIO
import pandas as pd
import joblib as jb
from datetime import datetime as dt

import spacy
from spacy.tokenizer import Tokenizer
from spacy.lang.es import Spanish
import es_core_news_lg

nlp = es_core_news_lg.load()
# contextualSpellCheck.add_to_pipe(nlp)
tokenizer = Tokenizer(nlp.vocab)
stop_words = nlp.Defaults.stop_words
stop_words.add('compensar_info')
stop_words.add('colsubsidio_ofi')
stop_words.add('cafamoficial')
stop_words.add('gracias')
stop_words.add('hola')


#======================================================================================================================================
#===============================      APP START    ====================================================================================
#======================================================================================================================================

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.config["suppress_callback_exceptions"] = True
app.title = 'Twitter sentyment analysis - Dashboard'

APP_PATH = str(pathlib.Path(__file__).parent.resolve())


#======================================================================================================================================
#===============================      DATA FRAMES   ===================================================================================
#======================================================================================================================================

df = jb.load(os.path.join(APP_PATH, os.path.join("data", "base_historica_calificada.joblib")))
df['popular']=df['replies']+df['retweets']+df['favorites']
df['date_2']=df['date'].apply(lambda x: x.tz_localize(None))
df['month']=df.date_2.dt.to_period("M")
df['month']=df.month.map(str)
caja_init=['Cafam','Colsubsidio','Compensar']



def filter_df(data):
    if len(data['check_caja'])==0:
        data['check_caja']=caja_init    
    
    df_temp=df[
    (df['name_caja'].isin(data['check_caja'])) & 
    (df['date_2'] >= data['start_date']) & 
    (df['date_2'] <= data['end_date'])&
    (search_query(data['query'], df))
    ]
    return df_temp

def sentiment_summary(data):
    di={'Negativo':'Negative','Positivo':'Positive','Neutro':'Neutral'}

    df_temp=filter_df(data)
    
    sentiment=df_temp.groupby('sentiment').count()['date'].reset_index()
    sentiment.columns=['sentiment','count']
    sentiment=sentiment.replace({'sentiment': di})
    sentiment=sentiment.set_index('sentiment')
    return sentiment

def month_summary(data):
    df_temp=filter_df(data)
    
    month=df_temp.groupby(['month','sentiment']).count()['date'].reset_index()
    month=month.pivot(index='month', columns='sentiment', values='date')
    return month

def pop_tweets_summary (data):
    di={'Negativo':'Negative','Positivo':'Positive','Neutro':'Neutral'}
    df_temp=filter_df(data)
    
    pop_tweets=df_temp.sort_values(by='popular',ascending=False).head(5)[['date','text','sentiment']].reset_index(drop=True)
    pop_tweets=pop_tweets.replace({'sentiment': di})
    return pop_tweets

def search_query(query, df):
    if (query == ''):
        df['cond_contiene'] = True
        return df['cond_contiene']
    token_query = list(tokenizer(query))
    tokens_for_search = [word for word in token_query if not word in stop_words]
    df['cond_contiene'] = False
    for token in tokens_for_search:
        df['cond_contiene'] = df['cond_contiene'] | df['chain_stop_words'].apply(lambda x: str(token) in x)
    return df['cond_contiene']


def init_df():
    data = {}
    data['check_caja']=[]
    data['start_date']=dt(2020,1,1)
    data['end_date']=max(df['date_2'])
    data['query']=''
    return data

state_dict = init_df()

def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict


#======================================================================================================================================
#===============================      CONSTRUCCION PAGINA      ========================================================================
#======================================================================================================================================


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                className="banner-logo",
                children=[
                    html.Img(id="logoTM", src=app.get_asset_url("team84.png")),
                ],
            ),
            html.Div(
                className="app-header",
                id="banner-text",
                children=[
                    html.H5('"CAJAS DE COMPENSACIÓN" TWITTER SENTIMENT'),
                    html.H6("Analysis of user's Tweets"),
                ],
            ),
            html.Div(
                className="banner-logo",
                children=[
                    html.Img(id="logoMT", src=app.get_asset_url("mintic.png")),
                    html.Img(id="logoDS", src=app.get_asset_url("ds4a2.png")),
                ],
            ),
        ],
    )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[ 
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Dashboard",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Specs-tab",
                        label="Team Information",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )


def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id="set-specs-intro-container",
            # className='twelve columns',
            children=html.P(
                "Use historical control limits to establish a benchmark, or set new values."
            ),
        ),
    ]

def build_quick_stats_panel(data):
    return html.Div(
        id="quick-stats",
        children=[
            generate_section_banner("Controls"),
            html.Div(
                id="card-0",
                children=[
                    html.P("Caja:", style={"font-weight": "bold"}),
                    dcc.Checklist(
                        id="check_caja",
                        options=[
                            {'label': 'Compensar', 'value': 'Compensar'},
                            {'label': 'Cafam', 'value': 'Cafam'},
                            {'label': 'Colsubsidio', 'value': 'Colsubsidio'}
                        ],
                        value=data['check_caja']
                    ),
                ],
            ),
            html.Div(
                id="card-0",
                children=[
                    html.P("Date Range:", style={"font-weight": "bold"}),
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=min(df['date_2']),
                        max_date_allowed=max(df['date_2']),
                        start_date=data['start_date'],
                        end_date=data['end_date'],
                        number_of_months_shown=2,
                        day_size= 50,
                        #with_portal=True,
                        style={"z-index":"100","max-width": "100%","font-size": "smaller"},
                    ),
                ],
            ),
            html.Div(
                id="card-0",
                children=[
                    html.P("Key Words:", style={"font-weight": "bold"}),
                    dcc.Input(
                        id="search",
                        placeholder="insert keywords",
                        value='',
                        style={"max-width": "100%","font-size": "smaller"},
                    ),
                ],
            ),
            generate_section_banner("Tweets Summary"),
            html.Div(
                id="card-1",
                children=[
                    html.P(
                        id="interactions",
                        style={"text-align": "center",
                            "font-size": "30px",
                            "font-weigh": "600",
                            "color": "rgb(55, 188, 200)",
                            "margin-bottom":"0",
                            },
                        children=[len(filter_df(data))],
                          ),
                    html.P("Interactions",
                          style={"text-align": "center",
                                "font-size": "12px",
                                "font-weigh": "100",
                                "color": "#BCCCDC",
                                "margin-top":"0",
                                },
                          ),
                ],
            ),
            html.Div(
                id="card-1",
                children=[
                    html.P(
                        id="users",
                        style={"text-align": "center",
                            "font-size": "30px",
                            "font-weigh": "600",
                            "color": "rgb(55, 188, 200)",
                            "margin-bottom":"0",
                            },
                        children=[ len(filter_df(data)['author_id'].unique())]
                          ),
                    html.P("Users",
                           style={"text-align": "center",
                                "font-size": "12px",
                                "font-weigh": "100",
                                "color": "#BCCCDC",
                                "margin-top":"0",
                                },
                          ),
                ],
            ),
        ],
        style={"display": "block",
              "padding":"0",},
    )


def generate_section_banner(title):
    return html.P(title,className="section-banner")
        
    


def build_top_panel(data):
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Word cloud
            html.Div(
                id="metric-summary-session",
                className="content-tile six columns",
                children=[
                    generate_section_banner("Most Frequent words"),
                    dcc.Loading(
                        children=[html.Img(id="image_wc",style={
                                        "max-width": "95%",
                                        "max-height":"90%",
                                        "margin_bottom":"1.5rem"}),
                                         ],
                        type="default",
                        color='#324d67ad',
                        #style={"margin":"auto"},
                    )
               ],
            ),
            
            # Piechart
            html.Div(
                className="content-tile six columns",
                children=[
                    generate_section_banner("Sentiment breakdown"),
                dcc.Loading(
                    children=[dcc.Graph(id="bar-graph",
                                        figure= generate_bar(data)
                                       ),
                             ],
                    type="default",
                    color='#324d67ad',
                    style={"margin":"auto"},
                ),                    
                    
               ],
                
            ),
            
        ],
    )




def build_chart_panel(data):
    return html.Div(
        id="control-chart-container",
        className="content-tile twelve columns",
        children=[
            generate_section_banner("Sentiment over time"),
            dcc.Loading(
                children=[dcc.Graph(id="line-graph",
                                    figure= generate_line(data)
                                   )
                         ],
                type="default",
                color='#324d67ad',
                style={"margin":"auto"},
            ),
        ],
    )


def build_tweet_card(i,data):
    pop_tweets=pop_tweets_summary(data)
    colors={'Negative':'rgb(187, 37, 37)','Positive':'rgb(20, 145, 153)','Neutral':'#f4d44d'}
    t_sentiment=pop_tweets.loc[i]['sentiment']
    t_text=pop_tweets.loc[i]['text']
    t_date=pop_tweets.loc[i]['date']
    s_color=colors[t_sentiment]
    
    return html.Div(
                    id="tweet-card",
                    children=[
                        html.Div(
                            id="tweet-head",
                            children=[html.P(t_date)],
                        ),
                        html.P(t_text,
                            style={"font-size": "0.8vw",
                                   "color": "hsl(209, 28%, 39%)",
                                   "padding-top": "25px",
                                   "margin-top": "0.5rem",
                                  },  
                        ),
                        html.Div(
                            id="tweet-sentiment",
                            children=[
                                html.P(t_sentiment,
                                    style={"background-color": s_color},
                                ),
                            ],
                        ),
                    ],
                    
                )
    
        

def build_relevant_tweets(data):
    return html.Div(
        className="content-tile",
        children=[
            generate_section_banner("Relevant tweets"),
            build_tweet_card(0,data),
            build_tweet_card(1,data),
            build_tweet_card(2,data),
        ],
        style={"margin-left": "1.8rem",},
    )


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=0,  # start at batch 50
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="value-setter-store", data=init_value_setter_store()),
        dcc.Store(id="n-interval-stage", data=50),   
    ],
)


@app.callback(
    [Output("app-content", "children"), Output("interval-component", "n_intervals")],
    [Input("app-tabs", "value")],
    [State("n-interval-stage", "data"),
     State("value-setter-store","data")],
)

def render_tab_content(tab_switch, stopped_interval,data):
    if tab_switch == "tab1":
        return  html.Div(
            className="content-tile",
            children=build_tab_1()
            ), stopped_interval
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(data),
                html.Div(
                    id="graphs-container",
                    children=[build_top_panel(data), build_chart_panel(data)],
                ),
                
                html.Div(
                    className = "content-tile",
                    style={ "width":        "25%",
                            "margin-left": "0.8rem",
                            "flex": "1 1",
                            "padding": "0rem",
                            #"background-color": "transparent",
                            "max-width": "25%",
                    },
                    children=[
                        dcc.Loading(
                            children=[
                                html.Div(id="tweets",
                                         children=[build_relevant_tweets(data)]
                                        )
                            ],
                        type="default",
                        color='#324d67ad',
                        style={"margin":"auto"},
                        ),
                    ],      
                ),
            ],
        ),
        stopped_interval,
    )

#======================================================================================================================================
#========================       GENERAR GRAFICAS         ==============================================================================
#======================================================================================================================================

def plot_wordcloud(data): #crea wordcloud
    wc = WordCloud(max_font_size=100, max_words=100, background_color="white",
                   scale = 10,width=380, height=290,
                   colormap="ocean").generate(data)
    return wc.to_image()



def generate_bar(data): # genera grafica de barras de sentimiento
    df_bar=sentiment_summary(data)
    total=df_bar['count'].sum()
    y_positive=round(df_bar.loc['Positive'].values[0]/total, 2)
    y_negative=round(df_bar.loc['Negative'].values[0]/total, 2)
    y_neutral=round(df_bar.loc['Neutral'].values[0]/total, 2)
    
    fig = go.Figure(go.Bar(x=["positive"], y=[y_positive],text=str(y_positive)+' %',
                           textposition='auto', marker_color="rgb(20, 145, 153)"))
    fig.add_trace(go.Bar(x=["negative"], y=[y_negative],text=str(y_negative)+' %',
                         textposition='auto', marker_color="rgb(187, 37, 37)"))
    fig.add_trace(go.Bar(x=["neutral"], y=[y_neutral],text=str(y_neutral)+' %',
                         textposition='auto',marker_color="#f4d44d"))
    
    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'}, 
                      height=260,margin=dict(l=10,r=15,b=10,t=15,pad=4),showlegend=False,
                      plot_bgcolor = '#f1f6ff')
    return fig


def generate_line(data): # genera grafica de tiempo
    df_line=month_summary(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_line.index, y=df_line.Positivo,
                             mode='lines',
                             name='positive',
                             line=dict(color="rgb(20, 145, 153)"),
                            ))
    fig.add_trace(go.Scatter(x=df_line.index, y=df_line.Negativo,
                             mode='lines',
                             name='negative',
                             line=dict(color="rgb(187, 37, 37)"),
                            ))
    fig.add_trace(go.Scatter(x=df_line.index, y=df_line.Neutro,
                             mode='lines',
                             name='neutral',
                             line=dict(color="#f4d44d"),
                            ))
    
    fig.update_layout(height=260,margin=dict(l=10,r=15,b=10,t=15,pad=4),showlegend=False,plot_bgcolor = '#f1f6ff')
  
    return fig

#======================================================================================================================================
#===============================       CALLBACKS CONTROLs                   ===========================================================
#======================================================================================================================================

#Grafica de barras!
@app.callback(
    Output(component_id='bar-graph', component_property='figure'),
    [Input('value-setter-store','data')]
)
def update_output(data):
    return generate_bar(data)


#Grafica de lineas!
@app.callback(
    Output(component_id='line-graph', component_property='figure'),
    [Input('value-setter-store','data')]
)
def update_output(data):
    return generate_line(data)


#wordcloud
@app.callback(
    Output('image_wc', 'src'), 
    [Input('image_wc', 'id'), 
     Input('value-setter-store','data')],
)
def make_image(b, data): #genera la imagen del wordcloud
    df_temp=filter_df(data)
    df_wc= ''.join(df_temp.clean_text_to_word)
    img = BytesIO()
    plot_wordcloud(data=df_wc).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

#tweets
@app.callback(
    Output(component_id='tweets', component_property='children'),
    [Input('value-setter-store','data')]
)
def update_output(data):
    return build_relevant_tweets(data)

#quick-stats

#interactions
@app.callback(
    Output(component_id='interactions', component_property='children'),
    [Input('value-setter-store','data')]
)
def update_output(data):
    df_temp=filter_df(data)
    return str(len(df_temp))

#users
@app.callback(
    Output(component_id='users', component_property='children'),
    [Input('value-setter-store','data')]
)
def update_output(data):
    df_temp=filter_df(data)
    return str(len(df_temp['author_id'].unique()))

#Actualizar data con la información de los fltros
@app.callback(
    Output('value-setter-store','data'),
    [Input(component_id='check_caja', component_property='value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('search','value')],
    [State('value-setter-store','data')]
)
def test(input_value,start_date,end_date,search_value,data):
    data['check_caja']=input_value
    data['start_date']=start_date
    data['end_date']=end_date
    data['query']=search_value
    return data


#======================================================================================================================================
#======================================================      INTERVALS      ===========================================================
#======================================================================================================================================



def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval

    if tab_switch == "tab1":
        return cur_interval
    return cur_stage


def stop_production(n_clicks, current):
    if n_clicks == 0:
        return True, "start"
    return not current, "stop" if current else "start"






#======================================================================================================================================
#===============================      CORRER EL SERVIDOR      =========================================================================
#======================================================================================================================================

if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
