import tensorflow as tf
# MODEL = "recommender-smote-try-simple-I"

STAR_WEIGHT = 0.5
SENTIMENT_WEIGHT = 0.5
STARTING_PROFILE_SCORE = 0.5
COLD_START_AVG_REVIEW = 0.5

YOUTUBE_HIGH_THRES = 2_000_000
YOUTUBE_LOW_THRES = 100_000
TIKTOK_HIGH_THRES = 2_000_000
TIKTOK_LOW_THRES = 100_000
INSTAGRAM_HIGH_THRES = 1_000_000
INSTAGRAM_LOW_THRES = 50_000

inf_data = [
    {
        'id': 100,
        'categories': ["Gaming", "Sports", "Lifestyle"],
        'ig_followers': 10000000,
        'yt_followers': 10000000,
        'tt_followers': 10000000,
        'product': [
            {
                'id': 1,
                'price': 1000000000
            },
            {
                'id': 2,
                'price': 1000000000
            },
            {
                'id': 3,
                'price': 5000000000
            },
        ]
    },
    {
        'id': 200,
        'categories': ["Technology"],
        'ig_followers': 10,
        'tt_followers': 10,
        'product': [
            {
                'id': 1,
                'price': 100
            },
            {
                'id': 2,
                'price': 100
            }
        ]
    },
    {
        'id': 300,
        'categories': ["Gaming", "Sports", "Lifestyle", "Technology"],
        'ig_followers': 10000000,
        'yt_followers': 10000000,
        'tt_followers': 10000000,
        'product': [
            {
                'id': 1,
                'price': 100000000
            },
            {
                'id': 2,
                'price': 10000000000
            },
            {
                'id': 3,
                'price': 5000000000000
            },
        ]
    },
    {
        'id': 400,
        'categories': ["Gaming", "Sports", "Lifestyle", "Technology"],
        'ig_followers': 10000,
        'yt_followers': 10000,
        'tt_followers': 10000,
        'product': [
            {
                'id': 1,
                'price': 1000000
            },
            {
                'id': 2,
                'price': 10000000
            },
            {
                'id': 3,
                'price': 5000
            },
        ]
    }
]

own_data = [
    {
        'id': 1,
        'categories': ["Gaming", "Sports", "Lifestyle", "Technology"]
    },
    {
        'id': 2,
        'categories': ['Education', 'Entertainment']
    },
    {
        'id': 3,
        'categories': ['Lifestyle']
    },
]

reviews = [
    {
        'own_id': 1,
        'inf_id': 100,
        'rating': 5,
        'review': "Kontennya bagus! Professional!",
        'sentiment_rating': 1
    },
    {
        'own_id': 1,
        'inf_id': 300,
        'rating': 5,
        'review': "Lumayan, responnya cepet",
        'sentiment_rating': 1
    },
    # {
    #     'own_id': 2,
    #     'inf_id': 200,
    #     'rating': 5,
    #     'review': "OK!",
    #     'sentiment_rating': 0.5
    # },
]


INF_PROFILE = ['avg_rating', 'pricing_LOW', 'pricing_BELOW_AVG', 'pricing_AVG',
        'pricing_ABOVE_AVG', 'pricing_HIGH', 'Food and Drinks', 'Sports',
        'Health', 'Technology', 'Beauty and Fashion', 'Gaming', 'Lifestyle',
        'Travel', 'Education', 'Entertainment', 'yt_followers_High', 'yt_followers_Low',
        'yt_followers_Medium', 'tt_followers_High', 'tt_followers_Low', 'tt_followers_Medium',
        'ig_followers_High', 'ig_followers_Low', 'ig_followers_Medium']

USER_PROFILE = ['pricing_LOW', 'pricing_BELOW_AVG', 'pricing_AVG', 'pricing_ABOVE_AVG',
        'pricing_HIGH', 'Food and Drinks', 'Sports', 'Health', 'Technology',
        'Beauty and Fashion', 'Gaming', 'Lifestyle', 'Travel', 'Education',
        'Entertainment', 'yt_followers_High', 'yt_followers_Low', 'yt_followers_Medium',
        'tt_followers_High', 'tt_followers_Low', 'tt_followers_Medium', 'ig_followers_High',
        'ig_followers_Low', 'ig_followers_Medium']

CATEGORIES = ['Food and Drinks', 'Sports', 'Health', 'Technology',
        'Beauty and Fashion', 'Gaming', 'Lifestyle', 'Travel', 'Education',
        'Entertainment']

import pandas as pd

def get_review_from_own_id(own_id):
    result = []
    for review in reviews:
        if (review['own_id'] == own_id):
            result.append(review)

    return result

# get_business_owner() -> get categorynya
def get_categories_from_own_id(own_id):
    for data in own_data:
        if (data['id'] == own_id):
            return data['categories']
        
# 1. get_influencer_by_username() -> {'avg_rating': 4.5} / 5
# 2. get_influencer_review() -> looping
def get_average_rating(inf_id):
    result = 0
    i = 0
    for review in reviews:
        if (review['inf_id'] == inf_id):
            result += STAR_WEIGHT * review['rating'] / 5+ SENTIMENT_WEIGHT * review['sentiment_rating']
            i += 1

    if (i != 0):
        return result / i
    else:
        return COLD_START_AVG_REVIEW

def get_influencer_recommender_profile(inf_id):
    YOUTUBE_HIGH_THRES = 2_000_000
    YOUTUBE_LOW_THRES = 100_000
    TIKTOK_HIGH_THRES = 2_000_000
    TIKTOK_LOW_THRES = 100_000
    INSTAGRAM_HIGH_THRES = 1_000_000
    INSTAGRAM_LOW_THRES = 50_000

    influencer = None
    for inf in inf_data:
        if (inf['id'] == inf_id):
            influencer = inf
            break

    if (influencer == None):
        print("Influencer not found")
        return
    
    inf_profile = pd.DataFrame(STARTING_PROFILE_SCORE, index=[inf_id], columns=INF_PROFILE, dtype=float)
    inf_profile.loc[inf_id][influencer['categories']] = 1

    # One hot followers
    if (influencer.get('yt_followers', 0) > YOUTUBE_HIGH_THRES):
        inf_profile.loc[inf_id]['yt_followers_High'] = 1
    elif (influencer.get('yt_followers', 0) > YOUTUBE_LOW_THRES):
        inf_profile.loc[inf_id]['yt_followers_Medium'] = 1
    else:
        inf_profile.loc[inf_id]['yt_followers_Low'] = 1

    if (influencer.get('ig_followers', 0) > INSTAGRAM_HIGH_THRES):
        inf_profile.loc[inf_id]['ig_followers_High'] = 1
    elif (influencer.get('ig_followers', 0) > INSTAGRAM_LOW_THRES):
        inf_profile.loc[inf_id]['ig_followers_Medium'] = 1
    else:
        inf_profile.loc[inf_id]['ig_followers_Low'] = 1
    
    if (influencer.get('tt_followers', 0) > TIKTOK_HIGH_THRES):
        inf_profile.loc[inf_id]['tt_followers_High'] = 1
    elif (influencer.get('tt_followers', 0) > TIKTOK_LOW_THRES):
        inf_profile.loc[inf_id]['tt_followers_Medium'] = 1
    else:
        inf_profile.loc[inf_id]['tt_followers_Low'] = 1

    # Get price categories
    for product in influencer['product']:
        if (product['price'] > 20_000_000):
            inf_profile.loc[inf_id]['price_HIGH'] = 1
        elif (product['price'] > 10_000_000):
            inf_profile.loc[inf_id]['price_ABOVE_AVG'] = 1
        elif (product['price'] > 5_000_000):
            inf_profile.loc[inf_id]['price_AVG'] = 1
        elif (product['price'] > 1_000_000):
            inf_profile.loc[inf_id]['price_BELOW_AVG'] = 1
        else:
            inf_profile.loc[inf_id]['price_LOW'] = 1

    inf_profile['avg_rating'] = get_average_rating(inf_id)

    return inf_profile

def one_hot(df, column):
    one_hot = df[column].str.get_dummies()
    col_name = one_hot.columns
    new_name = list(map(lambda name: column + "_" + name, col_name))
    one_hot.rename(columns={k: v for k, v in zip(col_name, new_name)}, inplace=True)

    df = pd.concat([df, one_hot], axis=1)
    df = df.drop(column, axis=1)

    return df

def one_hot_price(products):
    one_hot = []
    for product in products:
        if (product['price'] > 20_000_000):
            one_hot.append('pricing_HIGH')
        elif (product['price'] > 10_000_000):
            one_hot.append('pricing_ABOVE_AVG')
        elif (product['price'] > 5_000_000):
            one_hot.append('pricing_AVG')
        elif (product['price'] > 1_000_000):
            one_hot.append('pricing_BELOW_AVG')
        else:
            one_hot.append('pricing_LOW')

    return list(set(one_hot))

def get_all_influencer_recommender_profile(influencers):
    # Convert to pandas dataframe
    df_inf = pd.DataFrame(influencers).fillna(0)
    df_inf = df_inf.drop(["photo_profile_url", "ig_username", "password", "email", "address", "reviews", "yt_username", "tt_username"], axis=1)

    # Convert categories
    one_hot_categories = pd.get_dummies(df_inf['categories'].apply(pd.Series).stack()).groupby(level=0).sum()
    df_inf = pd.concat([df_inf, one_hot_categories], axis=1)
    df_inf = df_inf.drop('categories', axis=1)

    # Convert follower count
    youtube_bin = [0, YOUTUBE_LOW_THRES, YOUTUBE_HIGH_THRES, 100_000_000_000]
    tiktok_bin = [0, TIKTOK_LOW_THRES, TIKTOK_HIGH_THRES, 100_000_000_000]
    insta_bin = [0, INSTAGRAM_LOW_THRES, INSTAGRAM_HIGH_THRES, 100_000_000_000]

    print (youtube_bin)

    df_inf['yt_followers'] = pd.cut(df_inf['yt_followers'],bins=youtube_bin, labels=["Low", "Medium", "High"])  
    df_inf = one_hot(df_inf, 'yt_followers') 

    df_inf['tt_followers'] = pd.cut(df_inf['tt_followers'],bins=tiktok_bin, labels=["Low", "Medium", "High"])  
    df_inf = one_hot(df_inf, 'tt_followers') 

    df_inf['ig_followers'] = pd.cut(df_inf['ig_followers'],bins=insta_bin, labels=["Low", "Medium", "High"])  
    df_inf = one_hot(df_inf, 'ig_followers') 

    # Convert pricing
    df_inf['pricing'] = df_inf['products'].map(one_hot_price)
    one_hot_pricing = pd.get_dummies(df_inf['pricing'].apply(pd.Series).stack()).groupby(level=0).sum()
    df_inf = pd.concat([df_inf, one_hot_pricing], axis=1)
    df_inf = df_inf.drop(['products', 'pricing'], axis=1)

    # Get average rating
    df_inf['avg_rating'] = df_inf['username'].map(get_average_rating)

    df_inf = df_inf.reindex(columns=['username'] + INF_PROFILE).fillna(0).astype(float)

    return df_inf

# def get_all_owner_profile():

def get_combined_rating(rating, sentiment_rating    ):
    return STAR_WEIGHT * rating / 5 + SENTIMENT_WEIGHT * sentiment_rating

def get_user_recommender_profile(own_id):
    # Get categories
    one_hot_categories = pd.DataFrame([])
    one_hot_categories['categories'] = [get_categories_from_own_id(own_id)] 
    one_hot_categories = pd.get_dummies(one_hot_categories['categories'].apply(pd.Series).stack()).groupby(level=0).sum()

    # Get user reviews
    user_reviews = pd.DataFrame(get_review_from_own_id(own_id))
    if (len(user_reviews) != 0):
        user_reviews['combined_rating'] = get_combined_rating(user_reviews['rating'], user_reviews['sentiment_rating'])
        user_reviews = user_reviews.drop(['rating', 'sentiment_rating', 'review'], axis=1)
        df_inf = get_all_influencer_recommender_profile().drop('avg_rating', axis=1)

        # Multiply reviews with influencer's features
        user_profile = user_reviews.merge(df_inf, left_on='inf_id', right_on='id')
        user_profile[USER_PROFILE] = user_profile[USER_PROFILE].mul(user_profile['combined_rating'], axis=0)
        user_profile = user_profile.drop(['inf_id', 'id', 'combined_rating'], axis=1)

        # Get mean of each features as user profile
        user_profile = user_profile.groupby('own_id').sum()
        features_except_categories = list(set(user_profile.columns) - set(CATEGORIES))
        user_profile[features_except_categories] = user_profile[features_except_categories] / len(user_reviews)
        user_profile[CATEGORIES] = (user_profile[CATEGORIES] + one_hot_categories) / (len(user_reviews) + 1)
    else:
        user_profile = one_hot_categories

    # Reorder columns
    user_profile['id'] = own_id
    user_profile = user_profile.reindex(columns=['id'] + USER_PROFILE).fillna(0).astype(float)

    return user_profile

def get_all_user_recommender_profile():
    # Get categories
    users = pd.DataFrame(own_data)
    one_hot_categories = pd.get_dummies(users['categories'].apply(pd.Series).stack()).groupby(level=0).sum()
    one_hot_categories = pd.concat([users, one_hot_categories], axis=1)
    one_hot_categories.index = one_hot_categories['id']
    one_hot_categories = one_hot_categories.drop(['id', 'categories'], axis=1)
    
    # Get user reviews
    user_reviews = pd.DataFrame(reviews)
    user_reviews['combined_rating'] = get_combined_rating(user_reviews['rating'], user_reviews['sentiment_rating'])
    user_reviews = user_reviews.drop(['rating', 'sentiment_rating', 'review'], axis=1)
    user_reviews_count = user_reviews.groupby("own_id").count()['inf_id']
    user_reviews_count = user_reviews_count.reindex(users['id'], fill_value=0)
    df_inf = get_all_influencer_recommender_profile().drop('avg_rating', axis=1)

    # Multiply reviews with influencer's features
    user_profile = user_reviews.merge(df_inf, left_on='inf_id', right_on='id')
    user_profile[USER_PROFILE] = user_profile[USER_PROFILE].mul(user_profile['combined_rating'], axis=0)
    user_profile = user_profile.drop(['inf_id', 'id', 'combined_rating'], axis=1)

    # Get mean of each features as user profile
    user_profile = user_profile.groupby('own_id').sum()
    features_except_categories = list(set(user_profile.columns) - set(CATEGORIES))
    user_profile[features_except_categories] = user_profile[features_except_categories].div(user_reviews.groupby("own_id").count()['inf_id'], axis=0)
    user_profile = user_profile.combine_first(one_hot_categories).fillna(0)
    user_profile[CATEGORIES] = user_profile[CATEGORIES].div(user_reviews_count + 1, axis=0)
   
    # Reorder columns
    user_profile['id'] = user_profile.index
    user_profile = user_profile.reindex(columns=['id'] + USER_PROFILE).fillna(0).astype(float)

    return user_profile

# get_all_user_recommender_profile()

# Inference according to own_id
def get_owner_score_to_all_influencer(own_id, influencers):
    export_path = "recommender-model"
    model = tf.saved_model.load(export_path)
    infer = model.signatures["serving_default"]

    inf_profile = get_all_influencer_recommender_profile(influencers)
    user_profile = get_user_recommender_profile(own_id)

    id = inf_profile['id']
    inputs = [{'inf_feature': tf.convert_to_tensor([inf], dtype=float), 
                'own_feature': tf.convert_to_tensor(user_profile.values[:, 1:], dtype=float)}
                for inf in inf_profile.values[:, 1:]]


    score = []
    for i, data in enumerate(inputs):
        score.append(infer(**data))
        print(f"UserID: {own_id}, Inf ID: {int(id[i])} ->", infer(**data)['dot_2'].numpy()[0, 0])

def get_influencer_score_for_all_owner(inf_id):
    export_path = "recommender-model"
    model = tf.saved_model.load(export_path)
    infer = model.signatures["serving_default"]

    inf_profile = get_influencer_recommender_profile(inf_id)
    user_profile = get_all_user_recommender_profile()

    id = user_profile['id'].values
    inputs = [{'inf_feature': tf.convert_to_tensor(inf_profile.values, dtype=float), 
                'own_feature': tf.convert_to_tensor([owner], dtype=float)}
                for owner in user_profile.values[:, 1:]]
    
    score = []
    for i, data in enumerate(inputs):
        score.append(infer(**data))
        print(f"UserID: {int(id[i])}, Inf ID: {inf_id} ->", infer(**data)['dot_2'].numpy()[0, 0])


# Entar recommender berarti harus update semua data usernya tiap:
# 1. Ada owner baru (update score buat 1 owner ke semua influencer)
# 2. Ada influencer baru (update score buat semua owner ke 1 influencer)
# 3. Ada review baru (update score buat semua owner ke 1 influencer)


# get_owner_score_to_all_influencer(1)
# print()
# get_influencer_score_for_all_owner(100)


# get_influencer_scores(1)