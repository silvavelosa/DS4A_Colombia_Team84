from datetime import datetime
from joblib import Parallel, delayed, dump, load
import pandas as pd
import GetOldTweets3 as got
import datetime as dt
from classifier import *

clf = SentimentClassifier()


######################################################################################################

def convert_tweet_df(tweet):
    dict_info_tweet = {}
    dict_info_tweet['author_id'] = tweet.author_id
    dict_info_tweet['date'] = tweet.date
    dict_info_tweet['favorites'] = tweet.favorites
    dict_info_tweet['formatted_date'] = tweet.formatted_date
    dict_info_tweet['geo'] = tweet.geo
    dict_info_tweet['hashtags'] = tweet.hashtags
    dict_info_tweet['id'] = tweet.id
    dict_info_tweet['mentions'] = tweet.mentions
    dict_info_tweet['permalink'] = tweet.permalink
    dict_info_tweet['replies'] = tweet.replies
    dict_info_tweet['retweets'] = tweet.retweets
    dict_info_tweet['text'] = tweet.text
    dict_info_tweet['to'] = tweet.to
    dict_info_tweet['urls'] = tweet.urls
    dict_info_tweet['username'] = tweet.username
    return (dict_info_tweet)


def got_tweets(query, date_since, date_until):
    cons_tweet = got.manager.TweetCriteria().setQuerySearch(query) \
        .setSince(date_since) \
        .setUntil(date_until) \
        .setMaxTweets(-1)
    tweets = got.manager.TweetManager.getTweets(cons_tweet)
    return (tweets)


def get_range_dates(begin_date, end_date):
    # begin = '2018-01-01'
    # end = '2018-05-01'
    dt_start = dt.datetime.strptime(begin_date, '%Y-%m-%d')
    dt_end = dt.datetime.strptime(end_date, '%Y-%m-%d')
    one_day = dt.timedelta(1)
    start_dates = [dt_start]
    end_dates = []
    today = dt_start
    while today <= dt_end:
        # print(today)
        tomorrow = today + one_day
        if tomorrow.month != today.month:
            start_dates.append(tomorrow)
            end_dates.append(today)
        today = tomorrow
    end_dates.append(dt_end)
    start_date_text = [date.strftime('%Y-%m-%d') for date in start_dates]
    end_date_text = [date.strftime('%Y-%m-%d') for date in end_dates]
    return (start_date_text, end_date_text)


def get_all_tweets(query, date_since, date_until, name_caja, n_jobs_func=24):
    comienzo_periodo, fin_periodo = get_range_dates(date_since, date_until)
    scraped_tweets = Parallel(n_jobs=n_jobs_func, prefer="threads", verbose=100)(
        delayed(got_tweets)(query, fec_start, fec_end) for fec_start, fec_end in zip(comienzo_periodo, fin_periodo))
    flat_tweets = [item for sublist in scraped_tweets for item in sublist]
    df_tweets_hist = pd.DataFrame(map(convert_tweet_df, flat_tweets))
    df_tweets_hist['name_caja'] = name_caja
    return df_tweets_hist


def clean_tweets_compensar(df):
    df['date'] = pd.to_datetime(df['date'])
    df['text_clean'] = df['text'].apply(lambda x: str.lower(x))
    df['text_clean'] = df['text_clean'].str.replace(' m. familiar ', ' medicina familiar ')
    df['text_clean'] = df['text_clean'].str.replace(' m ', ' me ')
    df['text_clean'] = df['text_clean'].str.replace(' bb ', ' bebe ')
    df['text_clean'] = df['text_clean'].str.replace(' bn ', ' bien ')
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("u\\.u", " que decepción ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\\.", "", x))
    df['text_clean'] = df['text_clean'].str.replace('http\S+', ' ')
    df['text_clean'] = df['text_clean'].str.replace('[^\w\s]', ' ')
    df['text_clean'] = df['text_clean'].str.replace(' cc ', ' documento de identificación ')
    df['text_clean'] = df['text_clean'].str.replace(' cm ', ' administrador de la cuenta ')
    df['text_clean'] = df['text_clean'].str.replace(' inf ', ' información ')
    df['text_clean'] = df['text_clean'].str.replace(' num ', ' numero ')
    df['text_clean'] = df['text_clean'].str.replace(' d ', ' de ')
    df['text_clean'] = df['text_clean'].str.replace(' x ', ' por ')
    df['text_clean'] = df['text_clean'].str.replace(' k ', ' que ')
    df['text_clean'] = df['text_clean'].str.replace(' q ', ' que ')
    df['text_clean'] = df['text_clean'].str.replace(' xq ', ' por que ')
    df['text_clean'] = df['text_clean'].str.replace(' xa ', ' para ')
    df['text_clean'] = df['text_clean'].str.replace(' min ', ' minutos ')
    df['text_clean'] = df['text_clean'].str.replace(' hrs ', ' horas ')
    df['text_clean'] = df['text_clean'].str.replace(' atn ', ' atención ')
    df['text_clean'] = df['text_clean'].str.replace(' dra ', ' doctora ')
    df['text_clean'] = df['text_clean'].str.replace(' srs ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' sres ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace('srs ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace('sres ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' sr ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' pag ', ' pagina ')
    df['text_clean'] = df['text_clean'].str.replace(' fvr ', ' favor ')
    df['text_clean'] = df['text_clean'].str.replace(' dr ', ' doctor ')
    df['text_clean'] = df['text_clean'].str.replace(' med ', ' medico ')
    df['text_clean'] = df['text_clean'].str.replace(' porq ', ' porque ')
    df['text_clean'] = df['text_clean'].str.replace(' pa ', ' para ')
    df['text_clean'] = df['text_clean'].str.replace(' urg ', ' urgencias ')
    df['text_clean'] = df['text_clean'].str.replace(' plan obligatorio de salud ', ' doctor ')
    df['text_clean'] = df['text_clean'].str.replace(' dm ', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace('dm ', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace(' dm', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace(' a al u ', ' atención al usuario ')
    df['text_clean'] = df['text_clean'].str.replace(' at al u ', ' atención al usuario ')
    df['text_clean'] = df['text_clean'].str.replace('uds ', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' uds', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' uds ', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' ud ', ' usted ')
    df['text_clean'] = df['text_clean'].str.replace(' ej ', ' ejemplo ')
    df['text_clean'] = df['text_clean'].str.replace(' fa ', ' favor ')
    df['text_clean'] = df['text_clean'].str.replace(' hv ', ' hoja de vida ')
    df['text_clean'] = df['text_clean'].str.replace(' tel ', ' telefono ')
    df['text_clean'] = df['text_clean'].str.replace(' gbno ', ' gobierno ')
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\scompensar\s", " compensar_info ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("compensar\s", "compensar_info ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\scompensar$", "compensar_info ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\spc\s", " plan complementario ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub('\s+', ' ', x))
    # word = word.replace(' x ', ' por ')
    # word = word.replace(' q ', ' que ')
    # word = word.replace(' k ', ' que ')
    df['text_clean'] = df['text_clean'].apply(lambda x: x.rstrip())
    df['text_clean'] = df['text_clean'].apply(lambda x: x.lstrip())
    mask = ~df['text_clean'].str.contains('compensar_info') & df['username'] == 'Compensar_info'
    df.loc[mask, 'text_clean'] = df.loc[mask, 'text_clean'].apply(lambda x: 'compensar_info '.join(x))
    return df


def clean_tweets_colsubsidio(df):
    #df = tweets_colsubsidio
    df['date'] = pd.to_datetime(df['date'])
    df['text_clean'] = df['text'].apply(lambda x: str.lower(x))
    df['text_clean'] = df['text_clean'].str.replace(' m. familiar ', ' medicina familiar ')
    df['text_clean'] = df['text_clean'].str.replace(' m ', ' me ')
    df['text_clean'] = df['text_clean'].str.replace(' bb ', ' bebe ')
    df['text_clean'] = df['text_clean'].str.replace(' bn ', ' bien ')
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("u\\.u", " que decepción ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\\.", "", x))
    df['text_clean'] = df['text_clean'].str.replace('http\S+', ' ')
    df['text_clean'] = df['text_clean'].str.replace('[^\w\s]', ' ')
    df['text_clean'] = df['text_clean'].str.replace(' cc ', ' documento de identificación ')
    df['text_clean'] = df['text_clean'].str.replace(' cm ', ' administrador de la cuenta ')
    df['text_clean'] = df['text_clean'].str.replace(' inf ', ' información ')
    df['text_clean'] = df['text_clean'].str.replace(' num ', ' numero ')
    df['text_clean'] = df['text_clean'].str.replace(' d ', ' de ')
    df['text_clean'] = df['text_clean'].str.replace(' min ', ' minutos ')
    df['text_clean'] = df['text_clean'].str.replace(' x ', ' por ')
    df['text_clean'] = df['text_clean'].str.replace(' k ', ' que ')
    df['text_clean'] = df['text_clean'].str.replace(' q ', ' que ')
    df['text_clean'] = df['text_clean'].str.replace(' xq ', ' por que ')
    df['text_clean'] = df['text_clean'].str.replace(' xa ', ' para ')
    df['text_clean'] = df['text_clean'].str.replace(' hrs ', ' horas ')
    df['text_clean'] = df['text_clean'].str.replace(' atn ', ' atención ')
    df['text_clean'] = df['text_clean'].str.replace(' dra ', ' doctora ')
    df['text_clean'] = df['text_clean'].str.replace(' srs ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' sres ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace('srs ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace('sres ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' sr ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' pag ', ' pagina ')
    df['text_clean'] = df['text_clean'].str.replace(' fvr ', ' favor ')
    df['text_clean'] = df['text_clean'].str.replace(' dr ', ' doctor ')
    df['text_clean'] = df['text_clean'].str.replace(' med ', ' medico ')
    df['text_clean'] = df['text_clean'].str.replace(' porq ', ' porque ')
    df['text_clean'] = df['text_clean'].str.replace(' pa ', ' para ')
    df['text_clean'] = df['text_clean'].str.replace(' urg ', ' urgencias ')
    df['text_clean'] = df['text_clean'].str.replace(' plan obligatorio de salud ', ' doctor ')
    df['text_clean'] = df['text_clean'].str.replace(' dm ', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace('dm ', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace(' dm', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace(' a al u ', ' atención al usuario ')
    df['text_clean'] = df['text_clean'].str.replace(' at al u ', ' atención al usuario ')
    df['text_clean'] = df['text_clean'].str.replace('uds ', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' uds', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' uds ', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' ud ', ' usted ')
    df['text_clean'] = df['text_clean'].str.replace(' ej ', ' ejemplo ')
    df['text_clean'] = df['text_clean'].str.replace(' fa ', ' favor ')
    df['text_clean'] = df['text_clean'].str.replace(' hv ', ' hoja de vida ')
    df['text_clean'] = df['text_clean'].str.replace(' tel ', ' telefono ')
    df['text_clean'] = df['text_clean'].str.replace(' gbno ', ' gobierno ')
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\scolsubsidio\s", " colsubsidio_Ofi ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("colsubsidio\s", "colsubsidio_Ofi ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\scolsubsidio$", "colsubsidio_Ofi ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\spc\s", " plan complementario ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub('\s+', ' ', x))
    # word = word.replace(' x ', ' por ')
    # word = word.replace(' q ', ' que ')
    # word = word.replace(' k ', ' que ')
    df['text_clean'] = df['text_clean'].apply(lambda x: x.rstrip())
    df['text_clean'] = df['text_clean'].apply(lambda x: x.lstrip())
    mask = ~df['text_clean'].str.contains('colsubsidio_Ofi') & df['username'] == 'colsubsidio_Ofi'
    df.loc[mask, 'text_clean'] = df.loc[mask, 'text_clean'].apply(lambda x: 'colsubsidio_Ofi '.join(x))
    return df

def clean_tweets_cafam(df):
    df['date'] = pd.to_datetime(df['date'])
    df['text_clean'] = df['text'].apply(lambda x: str.lower(x))
    df['text_clean'] = df['text_clean'].str.replace(' m. familiar ', ' medicina familiar ')
    df['text_clean'] = df['text_clean'].str.replace(' m ', ' me ')
    df['text_clean'] = df['text_clean'].str.replace(' bb ', ' bebe ')
    df['text_clean'] = df['text_clean'].str.replace(' bn ', ' bien ')
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("u\\.u", " que decepción ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\\.", "", x))
    df['text_clean'] = df['text_clean'].str.replace('http\S+', ' ')
    df['text_clean'] = df['text_clean'].str.replace('[^\w\s]', ' ')
    df['text_clean'] = df['text_clean'].str.replace(' cc ', ' documento de identificación ')
    df['text_clean'] = df['text_clean'].str.replace(' cm ', ' administrador de la cuenta ')
    df['text_clean'] = df['text_clean'].str.replace(' inf ', ' información ')
    df['text_clean'] = df['text_clean'].str.replace(' num ', ' numero ')
    df['text_clean'] = df['text_clean'].str.replace(' d ', ' de ')
    df['text_clean'] = df['text_clean'].str.replace(' min ', ' minutos ')
    df['text_clean'] = df['text_clean'].str.replace(' x ', ' por ')
    df['text_clean'] = df['text_clean'].str.replace(' k ', ' que ')
    df['text_clean'] = df['text_clean'].str.replace(' q ', ' que ')
    df['text_clean'] = df['text_clean'].str.replace(' xq ', ' por que ')
    df['text_clean'] = df['text_clean'].str.replace(' xa ', ' para ')
    df['text_clean'] = df['text_clean'].str.replace(' hrs ', ' horas ')
    df['text_clean'] = df['text_clean'].str.replace(' atn ', ' atención ')
    df['text_clean'] = df['text_clean'].str.replace(' dra ', ' doctora ')
    df['text_clean'] = df['text_clean'].str.replace(' srs ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' sres ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace('srs ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace('sres ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' sr ', ' señores ')
    df['text_clean'] = df['text_clean'].str.replace(' pag ', ' pagina ')
    df['text_clean'] = df['text_clean'].str.replace(' fvr ', ' favor ')
    df['text_clean'] = df['text_clean'].str.replace(' dr ', ' doctor ')
    df['text_clean'] = df['text_clean'].str.replace(' med ', ' medico ')
    df['text_clean'] = df['text_clean'].str.replace(' porq ', ' porque ')
    df['text_clean'] = df['text_clean'].str.replace(' pa ', ' para ')
    df['text_clean'] = df['text_clean'].str.replace(' urg ', ' urgencias ')
    df['text_clean'] = df['text_clean'].str.replace(' plan obligatorio de salud ', ' doctor ')
    df['text_clean'] = df['text_clean'].str.replace(' dm ', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace('dm ', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace(' dm', ' mensaje directo ')
    df['text_clean'] = df['text_clean'].str.replace(' a al u ', ' atención al usuario ')
    df['text_clean'] = df['text_clean'].str.replace(' at al u ', ' atención al usuario ')
    df['text_clean'] = df['text_clean'].str.replace('uds ', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' uds', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' uds ', ' ustedes ')
    df['text_clean'] = df['text_clean'].str.replace(' ud ', ' usted ')
    df['text_clean'] = df['text_clean'].str.replace(' ej ', ' ejemplo ')
    df['text_clean'] = df['text_clean'].str.replace(' fa ', ' favor ')
    df['text_clean'] = df['text_clean'].str.replace(' hv ', ' hoja de vida ')
    df['text_clean'] = df['text_clean'].str.replace(' tel ', ' telefono ')
    df['text_clean'] = df['text_clean'].str.replace(' gbno ', ' gobierno ')
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\scafam\s", " cafamoficial ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("cafam\s", "cafamoficial ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\scafam$", "cafamoficial ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub("\spc\s", " plan complementario ", x))
    df['text_clean'] = df['text_clean'].apply(lambda x: re.sub('\s+', ' ', x))
    # word = word.replace(' x ', ' por ')
    # word = word.replace(' q ', ' que ')
    # word = word.replace(' k ', ' que ')
    df['text_clean'] = df['text_clean'].apply(lambda x: x.rstrip())
    df['text_clean'] = df['text_clean'].apply(lambda x: x.lstrip())
    mask = ~df['text_clean'].str.contains('cafamoficial') & df['username'] == 'cafamoficial'
    df.loc[mask, 'text_clean'] = df.loc[mask, 'text_clean'].apply(lambda x: 'cafamoficial '.join(x))
    return df

def calif_tweets(df,caja):
    if(caja == "cafamoficial"):
        tweets_clean = clean_tweets_cafam(df)
    if (caja == "Colsubsidio_Ofi"):
        tweets_clean = clean_tweets_colsubsidio(df)
    if (caja == "Compensar_info"):
        tweets_clean = clean_tweets_compensar(df)
    #tweets_clean = clean_tweets(df)
    tweets_clean["calif_sentiment"] = tweets_clean["text_clean"].apply(lambda x: clf.predict(x))
    tweets_clean["calif_sentiment"] = (tweets_clean["calif_sentiment"] - 0.5) * 2
    tweets_clean["sentiment"] = pd.cut(tweets_clean["calif_sentiment"], bins=[-2, -0.5, 0.2, 2],
                                       labels=["Negativo", "Neutro", "Positivo"])
    return tweets_clean


def get_tweets_and_clasific(query, date_since, date_until, n_jobs_func, df_hist, name_caja, caja):
    base_new = get_all_tweets(query=query, date_since=date_since, name_caja=name_caja,
                              date_until=date_until, n_jobs_func=n_jobs_func)
    print("tweets obtenidos")
    mask_iden = ~(base_new['id'].isin(df_hist['id']))
    base_to_calif = base_new[mask_iden]
    base_new_calif = calif_tweets(df=base_to_calif, caja=caja)
    base_retorno = df_hist.append(base_new_calif)
    return base_retorno


def get_tweets_and_clasific_several(consultas, date_since, date_until, n_jobs_func, df_hist):
    for cuenta, nombre in zip(consultas['cuenta'], consultas['nombre']):
        q = "".join(['(to:', cuenta, ") (@", cuenta, ")"])
        print(nombre)
        df_hist = get_tweets_and_clasific(query=q, date_since=date_since, date_until=date_until,
                                          n_jobs_func=n_jobs_func, df_hist=df_hist, name_caja=nombre,
                                          caja=cuenta)
        df_hist = df_hist.reset_index(drop=True)
    return df_hist



###################################################################################
###LOAD DATA TWEETS
with open('./data/base_historica_calificada.joblib', 'rb') as f:
    tweets_historicos = joblib.load(f)
#######LOAD CUENTAS
with open('./data/consultas_tweets.xlsx', 'rb') as f:
    consultas = pd.read_excel(f)
####################################################################################

hoy = datetime.today().strftime('%Y-%m-%d')
inicio = datetime.today() - dt.timedelta(3)
inicio = inicio.strftime('%Y-%m-%d')

resultado = get_tweets_and_clasific_several(consultas=consultas, date_since=inicio, date_until=hoy,
                                            n_jobs_func=1, df_hist=tweets_historicos
                                            )

with open('./data/base_historica_calificada.joblib', 'wb') as f:
    dump(resultado, f)
