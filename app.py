import os
import pathlib
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import dash_daq as daq
from wordcloud import WordCloud
from io import BytesIO
import pandas as pd
import joblib as jb


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
df['month']=df.date.dt.to_period("M")
df['month']=df.month.map(str)


params = list(df)
max_length = len(df)


t_sentiment='negative'
t_text="@Compensar_info buenos días. Tengo inconveniente con la afiliación de un empleado y no encuentro un canal para solucionar. ¿Por favor me podría colaborar?"
t_date='04:59:57 - Jul 18, 2020'
s_color="rgb(187, 37, 37)"


def sentiment_summary(df_tweets):
    di={'Negativo':'Negative','Positivo':'Positive','Neutro':'Neutral'}
    sentiment=df_tweets.groupby('sentiment').count()['date'].reset_index()
    sentiment.columns=['sentiment','count']
    sentiment=sentiment.replace({'sentiment': di})
    sentiment=sentiment.set_index('sentiment')
    return sentiment


def month_summary(df_tweets):
    month=df_tweets.groupby(['month','sentiment']).count()['date'].reset_index()
    month=month.pivot(index='month', columns='sentiment', values='date')
    return month

def pop_tweets_summary (df_tweets):
    di={'Negativo':'Negative','Positivo':'Positive','Neutro':'Neutral'}
    pop_tweets=df.sort_values(by='popular',ascending=False).head(5)[['date','text','sentiment']].reset_index(drop=True)
    pop_tweets=pop_tweets.replace({'sentiment': di})
    return pop_tweets


def init_df():
    ret = {}

    return ret

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

def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        children=[
            generate_section_banner("Tweets Summary"),
            html.Div(
                id="card-0",
                children=[
                    html.P("10%",
                          style={"text-align": "center",
                                "font-size": "30px",
                                "font-weigh": "600",
                                "color": "rgb(55, 188, 200)",
                                "margin-bottom":"0",
                                },
                          ),
                    html.P("Sentiment",
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
                    html.P(str(len(df)),
                          style={"text-align": "center",
                                "font-size": "30px",
                                "font-weigh": "600",
                                "color": "rgb(55, 188, 200)",
                                "margin-bottom":"0",
                                },
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
                id="card-2",
                children=[
                    html.P("7500",
                          style={"text-align": "center",
                                "font-size": "30px",
                                "font-weigh": "600",
                                "color": "rgb(55, 188, 200)",
                                "margin-bottom":"0",
                                },
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
        
    


def build_top_panel():
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
                    html.Img(id="image_wc",style={
                            "max-width": "95%",
                            "max-height":"90%"
                            }),
                ],
            ),
            
            # Piechart
            html.Div(
                className="content-tile six columns",
                children=[
                    generate_section_banner("Sentiment breakdown"),
                    dcc.Graph(figure= generate_bar(df)),
               ],
                
            ),
            
        ],
    )




def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="content-tile twelve columns",
        children=[
            generate_section_banner("Sentiment over time"),
            dcc.Graph(figure= generate_line(df)
                
            ),
        ],
    )


def build_tweet_card(i):
    pop_tweets=pop_tweets_summary(df)
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
                            style={"font-size": "0.88vw",
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
    
        

def build_relevant_tweets():
    return html.Div(
        className="content-tile",
        children=[
            generate_section_banner("Relevant tweets"),
            build_tweet_card(0),
            build_tweet_card(1),
            build_tweet_card(2),
            build_tweet_card(3),
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
            n_intervals=50,  # start at batch 50
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
    [State("n-interval-stage", "data")],
)

def render_tab_content(tab_switch, stopped_interval):
    if tab_switch == "tab1":
        return  html.Div(
            className="content-tile",
            children=build_tab_1()
            ), stopped_interval
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_top_panel(), build_chart_panel()],
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
                        build_relevant_tweets(),
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
                   scale = 10,width=320, height=300,
                   colormap="ocean").generate(data)
    return wc.to_image()


@app.callback(Output('image_wc', 'src'), [Input('image_wc', 'id')])
def make_image(b): #genera la imagen del wordcloud
    df_wc= ''.join(df.text)
    img = BytesIO()
    plot_wordcloud(data=df_wc).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


def generate_bar(df_tweets): # genera grafica de barras de sentimiento
    df_bar=sentiment_summary(df_tweets)
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


def generate_line(df_tweets): # genera grafica de tiempo
    df_line=month_summary(df_tweets)
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
#===============================      NO ENTIENDO PARA QUE FUNCIONA!!!      ===========================================================
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


# ======= Callbacks for modal popup =======

def update_click_output(button_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    return {"display": "none"}



#======================================================================================================================================
#===============================      CORRER EL SERVIDOR      =========================================================================
#======================================================================================================================================

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
