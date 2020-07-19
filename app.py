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




df_tweets=jb.load("tweets_sentiment_parse.joblib")
sentiment=df_tweets.groupby('sentiment').count()['watson_sentiment'].reset_index()
sentiment=sentiment[sentiment.sentiment.isin (['negative','neutral','positive'])]
date=df_tweets.groupby([df_tweets.date.dt.to_period("M"),'sentiment']).count()\
    ['watson_sentiment'].reset_index()

date['date']=date.date.map(str)
df2=date.pivot(index='date', columns='sentiment', values='watson_sentiment')
dfm= ''.join(df_tweets.text)

df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "spc_data.csv")))

params = list(df)
max_length = len(df)




t_sentiment='negative'
t_text="@Compensar_info buenos días. Tengo inconveniente con la afiliación de un empleado y no encuentro un canal para solucionar. ¿Por favor me podría colaborar?"
t_date='04:59:57 - Jul 18, 2020'
s_color="rgb(187, 37, 37)"


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
                    html.P(str(len(df_tweets)),
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
                    html.Div(
                        children=[
                            html.Img(id="image_wc",style={
                            "width": "95%",
                            "height":"95%"
                            }),
                        ],
                    ),
                ],
            ),
            
            # Piechart
            html.Div(
                className="content-tile six columns",
                children=[
                    generate_section_banner("Sentiment breakdown"),
                    dcc.Graph(figure= generate_bar()),
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
            dcc.Graph(figure= dict({
                    "data": [{"mode": "lines+markers",
                            "x": df2.index,
                            "y": df2.positive,
                            "name":'positive',
                            "line": {"color": "rgb(20, 145, 153)"}
                            },
                            {"mode": "lines+markers",
                            "x": df2.index,
                            "y": df2.negative,
                            "name":'negative',
                            "line": {"color": "rgb(187, 37, 37)"}
                            },
                            {"mode": "lines+markers",
                            "x": df2.index,
                            "y": df2.neutral,
                            "name":'neutral',
                            "line": {"color": "#f4d44d"}
                            }]
                })
            ),
        ],
    )


def build_tweet_card(t_sentiment, t_text,t_date):
    return html.Div(
                    id="tweet-card",
                    children=[
                        html.Div(
                            id="tweet-head",
                            children=[html.P(t_date)],
                        ),
                        html.P(t_text,
                            style={"font-size": "14px",
                                   "font-size": "1vw",
                                   "color": "hsl(209, 28%, 39%)",
                                   "padding-top": "25px",
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
            build_tweet_card(t_sentiment, t_text,t_date),
            build_tweet_card(t_sentiment, t_text,t_date),
            build_tweet_card(t_sentiment, t_text,t_date),
            build_tweet_card(t_sentiment, t_text,t_date),
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
                   scale = 10,width=300, height=300,
                   colormap="ocean").generate(data)
    return wc.to_image()


@app.callback(Output('image_wc', 'src'), [Input('image_wc', 'id')])
def make_image(b): #genera la imagen del wordcloud
    img = BytesIO()
    plot_wordcloud(data=dfm).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


def generate_bar(): # genera grafica de barras de sentimiento
    fig = go.Figure(go.Bar(x=["positive"], y=[0.4], name='Positive', marker_color="rgb(20, 145, 153)"))
    fig.add_trace(go.Bar(x=["negative"], y=[0.2], name='Negative', marker_color="rgb(187, 37, 37)"))
    fig.add_trace(go.Bar(x=["neutral"], y=[0.4], name='Neutral', marker_color="#f4d44d"))
    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'}, 
                      height=260,margin=dict(l=10,r=10,b=10,t=10,pad=4),showlegend=False,)
    return fig


def generate_line(): # genera grafica de tiempo
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df2.index, y=df2.positive,
                             mode='lines',
                             name='positive',
                             color="rgb(20, 145, 153)",
                            ))
    fig.add_trace(go.Scatter(x=df2.index, y=df2.negative,
                             mode='lines',
                             name='negative',
                             color="rgb(187, 37, 37)",
                            ))
    fig.add_trace(go.Scatter(x=df2.index, y=df2.neutral,
                             mode='lines',
                             name='neutral',
                             color="#f4d44d",
                            ))
  
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
