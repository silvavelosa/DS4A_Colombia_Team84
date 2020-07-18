from twitter_scraper import Profile
from joblib import load, Parallel, delayed, dump
import pandas as pd


##########FUNCTIONS#############
def get_profile(usuario):
    """

    :param usuario: (str)
    """
    try:
        prof = Profile(usuario)
    except:
        prof = usuario + ' NO SE ENCONTRO'
    return (prof)


def convert_profile_todict(profile):
    """

    :type profile: twwet_class (profile de clase tweet)
    """
    dict_temp = profile.to_dict()
    dict_temp['location'] = profile.location
    return dict_temp


def get_pd_profiles(usuarios_caja, _n_jobs=20):
    profiles_caja = Parallel(n_jobs=_n_jobs, prefer="threads", verbose=100)(
        delayed(get_profile)(user) for user in usuarios_caja)
    profiles_completos = [profile for profile in profiles_caja if str(type(profile)) != "<class 'str'>"]
    profiles_noencontrados = [profile for profile in profiles_caja if str(type(profile)) == "<class 'str'>"]
    print(profiles_noencontrados)
    lista_dict = list(map(convert_profile_todict, profiles_completos))
    df_profiles = pd.DataFrame(lista_dict)
    return df_profiles

##########LOAD DATA#############
with open('./tweets_historicos/tweets_compensar.joblib', 'rb') as f:
    tweets_compensar = load(f)
##########EXTRACT USER#####################
usuarios_caja = tweets_compensar['username'].unique()
#########EXTRACT PROFILE INFO##############
df_profiles = get_pd_profiles(usuarios_caja)
with open('./tweets_historicos/perfiles_tweets_compensar.joblib', 'wb') as f:
    dump(df_profiles, f)