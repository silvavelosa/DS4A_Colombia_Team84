import GetOldTweets3 as got
import pandas as pd
import datetime as dt
from joblib import Parallel, delayed, dump, load


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


def get_all_tweets(query, date_since, date_until, n_jobs_func=24):
    comienzo_periodo, fin_periodo = get_range_dates(date_since, date_until)
    scraped_tweets = Parallel(n_jobs=n_jobs_func, prefer="threads", verbose=100)(
        delayed(got_tweets)(query, fec_start, fec_end) for fec_start, fec_end in zip(comienzo_periodo, fin_periodo))
    flat_tweets = [item for sublist in scraped_tweets for item in sublist]
    df_tweets_hist = pd.DataFrame(map(convert_tweet_df, flat_tweets))
    return (df_tweets_hist)


############A PARTIR DE AQUI SE CORRE PARA GENERAR Y GUARDAR EL ARCHIVO###########

data_final = get_all_tweets(query="(to:Compensar_info) (@Compensar_info)", date_since='2017-01-01',
                            date_until='2020-06-01')
with open('./tweets_historicos/tweets_compensar.joblib', 'wb') as f:
    dump(data_final, f)

##PRUEBA PARA EL CARGUE DEL ARCHIVO##
with open('./tweets_historicos/tweets_compensar.joblib', 'rb') as f:
    tweets_compensar = load(f)