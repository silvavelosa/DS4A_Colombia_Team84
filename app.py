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

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"

def plot_wordcloud(data):
    wc = WordCloud(max_font_size=100, max_words=100, background_color="white",\
                          scale = 10,width=300, height=300).generate(data)
    return wc.to_image()

@app.callback(Output('image_wc', 'src'), [Input('image_wc', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=dfm).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


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
                    html.H6("Analysis of user's Tweets from a week in June 2020"),
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


def init_df():
    ret = {}

    return ret

state_dict = init_df()


def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict


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
        className="row content-tile",
        children=[
            generate_section_banner("Tweets Summary"),
            html.Div(
                id="card-1",
                children=[
                    html.P("Total Tweet Count"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value=str(len(df_tweets)),
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=40,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Total User Count"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value="7129",
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=40,
                    ),
                ],
            ),
            #html.Div(
                #id="card-2",
                #children=[
                    #html.P("Time to completion"),
                    #daq.Gauge(
                        #id="progress-gauge",
                        #max=max_length * 2,
                        #min=0,
                        #showCurrentValue=True,  # default size 200 pixel
                    #),
                #],
            #),
            #html.Div(
                #id="utility-card",
                #children=[daq.StopButton(id="stop-button", size=160, #n_clicks=0)],
            #),"""

        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title,)


def build_top_panel(stopped_interval):
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
                        id="metric-div",
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
                id="ooc-piechart-outer",
                className="content-tile six columns",
                children=[
                    generate_section_banner("Sentiment breakdown"),
                    dcc.Graph(
                        id='piechart2',
                        figure= dict({
                            "data": [{"type": "pie",
                                    "labels": sentiment['sentiment'],
                                    "values": sentiment['watson_sentiment'],
                                     "marker": {'colors': [
                                                 '#de1738',
                                                 '#f4d44d',
                                                 '#05d44d'
                                                ]},
                                     }],
                            "layout": {"margin": dict(l=20, r=20, t=20, b=30),
                                       "autosize": True,
                                       "showlegend":False,
                                     }
                        })
                    ),
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
            dcc.Graph(
                id='example-graph_2',
                figure= dict({
                    "data": [{"mode": "lines+markers",
                            "x": df2.index,
                            "y": df2.positive,
                            "name":'positive',
                            "line": {"color": "#05d44d"}
                            },
                            {"mode": "lines+markers",
                            "x": df2.index,
                            "y": df2.negative,
                            "name":'negative',
                            "line": {"color": "#de1738"}
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

t_sentiment='negative'
t_text="@Compensar_info buenos días. Tengo inconveniente con la afiliación de un empleado y no encuentro un canal para solucionar. ¿Por favor me podría colaborar?"
t_date='04:59:57 - Jul 18, 2020'
s_color="rgb(187, 37, 37)"

def build_tweet_card(t_sentiment, t_text,t_date):
  
    return html.Div(
                    className="tweet-card",
                    style={ "height":"22rem",
                          "margin-bottom":"0.825rem",
                          "box-shadow":"0 4px 6px 0 hsla(0, 0%, 0%, 0.18)",
                          "overflow":"hidden",
                          "padding":"20px 16px 16px 16px",
                          "position":"relative",
                          "display":"flex",
                          "flex-direction":"column",
                          "min-width":"0",
                          "background-color":"#fff",
                          "border":"1px solid rgba(0,0,0,.125)",
                          "border-radius":".25rem",
                          },
                    children=[
                        html.Div(
                            html.P(
                                t_date,
                                style={ "position":"absolute",
                                        "top": "4px",
                                        "font-size": "14px",
                                        "font-size": "1vw",
                                        "color": "hsl(209, 23%, 60%)",
                                        "margin-bottom": "0",
                                      },
                            ),
                            style={"width": "100%",
                                "position": "absolute",
                                "top": "16px",
                                "right": "64px",
                                "left": "16px",
                                  },
                        ),
                        html.P(
                            t_text,
                            style={"font-size": "14px",
                                   "font-size": "1vw",
                                "color": "hsl(209, 28%, 39%)",
                                "padding-top": "25px",
                                  },  
                        ),
                        html.Div(
                            children=[
                                #insert retweets
                                #html.Img(id="rt", 
                                #         src=app.get_asset_url("retweet.png"),
                                #         style={
                                #             "position": "absolute",
                                #             "margin-left":".8em",
                                #             "bottom":"5px",
                                #             },
                                #        ),
                                #html.P("4"),
                                html.P(
                                    t_sentiment,
                                    style={
                                        "margin-right":".8em",
                                        "position": "absolute",
                                        "bottom":"5px",
                                        "right": "16px",
                                        "z-index": "1000",
                                        "background-color": s_color,
                                        "color": "#fff",
                                        "display": "inline-block",
                                        "padding": ".25em .4em",
                                        "font-weight": "700",
                                        "line-height": "1",
                                        "text-align": "center",
                                        "white-space": "nowrap",
                                        "vertical-align": "baseline",
                                        "border-radius": ".30rem",
                                        "transition": "color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out",
                                          },
                                ),
                            ],
                            style={"content": "" "",
                                "display": "block",
                                "background-color": "#FFF",
                                "height": "25px",
                                "width": "100%",
                                "position": "absolute",
                                "bottom": "0",
                                  },
                        ),
                    ],
                    
                )
    
        

def build_relevant_tweets():
    return html.Div(
        id="relevant-tweets-container",
        className="content-tile",
        children=[
            generate_section_banner("Relevant tweets"),
            build_tweet_card(t_sentiment, t_text,t_date),
            build_tweet_card(t_sentiment, t_text,t_date),
            build_tweet_card(t_sentiment, t_text,t_date),
        ],
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
                    children=[build_top_panel(stopped_interval), build_chart_panel()],
                ),
                html.Div(
                    className = "content-tile",
                    id="right-bar-summary",
                    style={ "width":        "25%",
                            "margin-left": "0.8rem",
                            "flex": "1 1",
                            "padding": "2rem",
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



# Update interval
@app.callback(
    Output("n-interval-stage", "data"),
    [Input("app-tabs", "value")],
    [
        State("interval-component", "n_intervals"),
        State("interval-component", "disabled"),
        State("n-interval-stage", "data"),
    ],
)
def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval

    if tab_switch == "tab1":
        return cur_interval
    return cur_stage


# Callbacks for stopping interval update
@app.callback(
    [Output("interval-component", "disabled"), Output("stop-button", "buttonText")],
    [Input("stop-button", "n_clicks")],
    [State("interval-component", "disabled")],
)
def stop_production(n_clicks, current):
    if n_clicks == 0:
        return True, "start"
    return not current, "stop" if current else "start"


# ======= Callbacks for modal popup =======
@app.callback(
    Output("markdown", "style"),
    [Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    return {"display": "none"}


# decorator for list of output
def create_callback(param):
    def callback(interval, stored_data):
        count, ooc_n, ooc_g_value, indicator = update_count(
            interval, param, stored_data
        )
        spark_line_data = update_sparkline(interval, param)
        return count, spark_line_data, ooc_n, ooc_g_value, indicator

    return callback


for param in params[1:]:
    update_param_row_function = create_callback(param)
    app.callback(
        output=[
            Output(param + suffix_count, "children"),
            Output(param + suffix_sparkline_graph, "extendData"),
            Output(param + suffix_ooc_n, "children"),
            Output(param + suffix_ooc_g, "value"),
            Output(param + suffix_indicator, "color"),
        ],
        inputs=[Input("interval-component", "n_intervals")],
        state=[State("value-setter-store", "data")],
    )(update_param_row_function)




# Update piechart
@app.callback(
    output=Output("piechart", "figure"),
    inputs=[Input("interval-component", "n_intervals")],
    state=[State("value-setter-store", "data")],
)
def update_piechart(interval, stored_data):
    if interval == 0:
        return {
            "data": [],
            "layout": {
                "font": {"color": "#000000"},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
            },
        }

    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval - 1

    new_figure = {
    }
    return new_figure


# Running the server
if __name__ == "__main__":
    app.run_server(debug=False, port=8050, host='0.0.0.0')
