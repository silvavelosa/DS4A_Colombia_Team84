import joblib
import pandas as pd
from classifier import *
clf = SentimentClassifier()
######################################################################################################
def clean_tweets(df):
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
###################################################################################
###LOAD DATA TWEETS
with open('./tweets_compensar.joblib', 'rb') as f:
    tweets_compensar = joblib.load(f)
#######
tweets_compensar_clean = clean_tweets(tweets_compensar)
tweets_compensar_clean["sentiment"] = tweets_compensar_clean["text_clean"].apply(lambda x: clf.predict(x))
tweets_compensar_clean["sentiment"] = (tweets_compensar_clean["sentiment"]-0.5)*2
















######################################################################################
data_clasificar = joblib.load("tweets_compensar_clean.joblib")
data_clasificar["sentiment"] = data_clasificar["text_clean"].apply(lambda x: clf.predict(x))
data_clasificar["sentiment"] = (data_clasificar["sentiment"]-0.5)*2


tabla_excel = pd.read_excel("E:/documentos_nicolas/prueba_watson.xlsx")

aa = data_clasificar.loc[tabla_excel["id_fila"]]

aa[["sentiment", "text"]].to_excel("score_modelo.xlsx")