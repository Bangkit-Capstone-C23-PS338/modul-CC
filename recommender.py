import tensorflow as tf
import pandas as pd
# MODEL = "recommender-smote-try-simple-I"
# TODO: Nambahin username dari owner di setiap review

STAR_WEIGHT = 0.5
SENTIMENT_WEIGHT = 0.5
STARTING_PROFILE_SCORE = 0.1
COLD_START_AVG_REVIEW = 0.5

YOUTUBE_HIGH_THRES = 2_000_000
YOUTUBE_LOW_THRES = 100_000
TIKTOK_HIGH_THRES = 2_000_000
TIKTOK_LOW_THRES = 100_000
INSTAGRAM_HIGH_THRES = 1_000_000
INSTAGRAM_LOW_THRES = 50_000


INF_PROFILE = ['avg_rating', 'pricing_LOW', 'pricing_BELOW_AVG', 'pricing_AVG',
        'pricing_ABOVE_AVG', 'pricing_HIGH', 'Food and Drinks', 'Sports',
        'Health', 'Technology', 'Beauty and Fashion', 'Gaming', 'Lifestyle',
        'Travel', 'Education', 'Entertainment', 'yt_followers_High', 'yt_followers_Low',
        'yt_followers_Medium', 'tt_followers_High', 'tt_followers_Low', 'tt_followers_Medium',
        'ig_followers_High', 'ig_followers_Low', 'ig_followers_Medium']

OWNER_PROFILE = ['pricing_LOW', 'pricing_BELOW_AVG', 'pricing_AVG', 'pricing_ABOVE_AVG',
        'pricing_HIGH', 'Food and Drinks', 'Sports', 'Health', 'Technology',
        'Beauty and Fashion', 'Gaming', 'Lifestyle', 'Travel', 'Education',
        'Entertainment', 'yt_followers_High', 'yt_followers_Low', 'yt_followers_Medium',
        'tt_followers_High', 'tt_followers_Low', 'tt_followers_Medium', 'ig_followers_High',
        'ig_followers_Low', 'ig_followers_Medium']

CATEGORIES = ['Food and Drinks', 'Sports', 'Health', 'Technology',
        'Beauty and Fashion', 'Gaming', 'Lifestyle', 'Travel', 'Education',
        'Entertainment']


def get_review_from_own_company_name(company_name, influencers):
    result = []
    for review in get_all_reviews(influencers):
        if (review['company_name'] == company_name):
            result.append(review)

    return result

def get_all_reviews(influencers):
    all_reviews = []
    for data in influencers:
        inf_review = data.get('reviews', [])
        all_reviews += [{**d, 'inf_username': data['username']} for d in inf_review]

    return all_reviews

# get_business_owner() -> get categorynya
# def get_categories_from_own_id(own_id):
#     for data in own_data:
#         if (data['id'] == own_id):
#             return data['categories']
        
# 1. get_influencer_by_username() -> {'avg_rating': 4.5} / 5
# 2. get_influencer_review() -> looping
def get_average_rating(username, influencers):
    reviews = []
    for influencer in influencers:
        if (influencer['username'] == username):
            reviews = influencer.get('reviews', [])
            break
    
    i = 0
    result = 0
    for review in reviews:
        result += STAR_WEIGHT * review.get('rating', 1) / 5 + SENTIMENT_WEIGHT * review.get('sentiment', 1)
        i += 1

    if (i != 0):
        return result / i
    else:
        return COLD_START_AVG_REVIEW

def get_influencer_recommender_profile(username, influencers):
    influencer = None
    for data in influencers:
        if (data['username'] == username):
            influencer = data
            break

    if (influencer == None):
        print("Influencer not found")
        return None
    
    inf_profile = pd.DataFrame(STARTING_PROFILE_SCORE, index=[username], columns=INF_PROFILE, dtype=float)
    inf_profile.loc[username][[x for x in influencer['categories'] if x in CATEGORIES]] = 1

    # One hot followers
    if (influencer.get('yt_followers', 0) > YOUTUBE_HIGH_THRES):
        inf_profile.loc[username]['yt_followers_High'] = 1
    elif (influencer.get('yt_followers', 0) > YOUTUBE_LOW_THRES):
        inf_profile.loc[username]['yt_followers_Medium'] = 1
    else:
        inf_profile.loc[username]['yt_followers_Low'] = 1

    if (influencer.get('ig_followers', 0) > INSTAGRAM_HIGH_THRES):
        inf_profile.loc[username]['ig_followers_High'] = 1
    elif (influencer.get('ig_followers', 0) > INSTAGRAM_LOW_THRES):
        inf_profile.loc[username]['ig_followers_Medium'] = 1
    else:
        inf_profile.loc[username]['ig_followers_Low'] = 1
    
    if (influencer.get('tt_followers', 0) > TIKTOK_HIGH_THRES):
        inf_profile.loc[username]['tt_followers_High'] = 1
    elif (influencer.get('tt_followers', 0) > TIKTOK_LOW_THRES):
        inf_profile.loc[username]['tt_followers_Medium'] = 1
    else:
        inf_profile.loc[username]['tt_followers_Low'] = 1

    # Get price categories
    for product in influencer['products']:
        if (product['price'] > 20_000_000):
            inf_profile.loc[username]['price_HIGH'] = 1
        elif (product['price'] > 10_000_000):
            inf_profile.loc[username]['price_ABOVE_AVG'] = 1
        elif (product['price'] > 5_000_000):
            inf_profile.loc[username]['price_AVG'] = 1
        elif (product['price'] > 1_000_000):
            inf_profile.loc[username]['price_BELOW_AVG'] = 1
        else:
            inf_profile.loc[username]['price_LOW'] = 1

    inf_profile['avg_rating'] = get_average_rating(username, influencers)

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
    df_inf = pd.DataFrame(influencers).fillna(STARTING_PROFILE_SCORE)
    df_inf = df_inf.drop(["userid", "photo_profile_url", "ig_username", "password", "email", "address", "reviews", "yt_username", "tt_username"], axis=1)

    # Convert categories
    one_hot_categories = pd.get_dummies(df_inf['categories'].apply(pd.Series).stack()).groupby(level=0).sum()
    df_inf = pd.concat([df_inf, one_hot_categories], axis=1)
    df_inf = df_inf.drop('categories', axis=1)

    # Convert follower count
    youtube_bin = [0, YOUTUBE_LOW_THRES, YOUTUBE_HIGH_THRES, 100_000_000_000]
    tiktok_bin = [0, TIKTOK_LOW_THRES, TIKTOK_HIGH_THRES, 100_000_000_000]
    insta_bin = [0, INSTAGRAM_LOW_THRES, INSTAGRAM_HIGH_THRES, 100_000_000_000]

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
    df_inf['avg_rating'] = df_inf['username'].apply(lambda x: get_average_rating(x, influencers))
    df_inf = df_inf.filter(['username'] + INF_PROFILE, axis=1)
    df_inf = df_inf.reindex(columns=['username'] + INF_PROFILE).fillna(STARTING_PROFILE_SCORE)

    return df_inf

def get_combined_rating(rating, sentiment_rating):
    if (type(sentiment_rating) == pd.Series):
      sentiment_rating = sentiment_rating.fillna(1)
    elif (sentiment_rating == None):
      sentiment_rating = 1
    return STAR_WEIGHT * rating / 5 + SENTIMENT_WEIGHT * sentiment_rating

def get_username_from_company_name(company_name, owners):
    username = owners[owners['company_name'] == company_name]['username'].values[0]
    return username

def get_owner_recommender_profile(username, influencers, owners):
    # Get owner
    owner = {}
    for data in owners:
        if (data['username'] == username):
            owner = data
            break
    
    if (owner == {}):
        print("Owner not found")
        return None
    
    # Get categories
    one_hot_categories = pd.DataFrame([])
    one_hot_categories['categories'] = [owner.get('categories', [])] 
    one_hot_categories = pd.get_dummies(one_hot_categories['categories'].apply(pd.Series).stack()).groupby(level=0).sum()

    # Get user reviews
    owner_reviews = pd.DataFrame(get_review_from_own_company_name(owner['company_name'], influencers))
    if (len(owner_reviews) != 0):
        owner_reviews['combined_rating'] = get_combined_rating(owner_reviews['rating'], owner_reviews.get('sentiment', 1))
        owner_reviews['own_username'] = username
        owner_reviews = owner_reviews[["own_username", "inf_username", "combined_rating"]]
        df_inf = get_all_influencer_recommender_profile(influencers).drop('avg_rating', axis=1)

        # Multiply reviews with influencer's features
        owner_profile = owner_reviews.merge(df_inf, left_on='inf_username', right_on='username')
        owner_profile[OWNER_PROFILE] = owner_profile[OWNER_PROFILE].mul(owner_profile['combined_rating'], axis=0)
        owner_profile = owner_profile.drop(['username', 'inf_username', 'combined_rating'], axis=1)

        # Get mean of each features as user profile
        owner_profile = owner_profile.groupby('own_username').sum()
        owner_profile[CATEGORIES] = (owner_profile[CATEGORIES] + one_hot_categories)
        owner_profile = owner_profile / len(owner_reviews)
    else:
        owner_profile = one_hot_categories

    # Reorder columns
    owner_profile = owner_profile.filter(OWNER_PROFILE, axis=1)
    owner_profile['username'] = username
    owner_profile = owner_profile.reindex(columns=['username'] + OWNER_PROFILE).fillna(STARTING_PROFILE_SCORE)

    return owner_profile

def get_all_owner_recommender_profile(influencers, owners):
    # Get categories
    owners = pd.DataFrame(owners)
    one_hot_categories = pd.get_dummies(owners['categories'].apply(pd.Series).stack()).groupby(level=0).sum()
    one_hot_categories = pd.concat([owners, one_hot_categories], axis=1)
    one_hot_categories.index = one_hot_categories['username']
    one_hot_categories = one_hot_categories.drop(['username', 'categories'], axis=1).filter(CATEGORIES, axis=1)
    
    # Get user reviews
    owner_reviews = pd.DataFrame(get_all_reviews(influencers))
    owner_reviews['combined_rating'] = get_combined_rating(owner_reviews['rating'], owner_reviews.get('sentiment', 1))
    owner_reviews = owner_reviews[["company_name", "inf_username", "combined_rating"]]
    owner_reviews['own_username'] = owner_reviews['company_name'].map(lambda x: get_username_from_company_name(x, owners))              #### TODO
    owner_reviews_count = owner_reviews.groupby("own_username").count()['inf_username']
    owner_reviews_count = owner_reviews_count.reindex(owners['username'], fill_value=0)    
    df_inf = get_all_influencer_recommender_profile(influencers).drop('avg_rating', axis=1)

    # Multiply reviews with influencer's features
    owner_profiles = owner_reviews.merge(df_inf, left_on='inf_username', right_on='username')
    owner_profiles[OWNER_PROFILE] = owner_profiles[OWNER_PROFILE].mul(owner_profiles['combined_rating'], axis=0)
    owner_profiles = owner_profiles.drop(['username', 'inf_username', 'combined_rating'], axis=1)

    # Get mean of each features as user profile
    owner_profiles = owner_profiles.groupby('own_username').sum()
    owner_profiles = owner_profiles.combine_first(one_hot_categories).fillna(STARTING_PROFILE_SCORE)
    owner_profiles = owner_profiles.div(owner_reviews_count + 1, axis=0)

   
    # Reorder columns
    owner_profiles = owner_profiles.filter(OWNER_PROFILE, axis=1)
    owner_profiles['own_username'] = owner_profiles.index
    owner_profiles = owner_profiles.reindex(columns=['own_username'] + OWNER_PROFILE).fillna(STARTING_PROFILE_SCORE)

    return owner_profiles

# get_all_owner_recommender_profile()

# Inference according to own_id
def get_owner_score_to_all_influencer(username, influencers, owners):
    export_path = "recommender-model"
    model = tf.saved_model.load(export_path)
    infer = model.signatures["serving_default"]

    inf_profile = get_all_influencer_recommender_profile(influencers)
    owner_profile = get_owner_recommender_profile(username, influencers, owners)

    inf_username = inf_profile['username']
    inputs = [{'inf_feature': tf.convert_to_tensor([inf], dtype=float), 
                'own_feature': tf.convert_to_tensor(owner_profile.values[:, 1:], dtype=float)}
                for inf in inf_profile.values[:, 1:]]

    score = []
    for data in inputs:
        score.append(infer(**data)['dot_2'].numpy()[0, 0])

    sorted_score, sorted_inf = zip(*sorted(zip(score, inf_username), reverse=True))
    return list(sorted_score), list(sorted_inf)

def get_influencer_score_for_all_owner(username, influencers, owners):
    export_path = "recommender-model"
    model = tf.saved_model.load(export_path)
    infer = model.signatures["serving_default"]

    inf_profile = get_influencer_recommender_profile(username, influencers)
    owner_profile = get_all_owner_recommender_profile(influencers, owners)    

    own_username = owner_profile['own_username'].values
    inputs = [{'inf_feature': tf.convert_to_tensor(inf_profile.values, dtype=float), 
                'own_feature': tf.convert_to_tensor([owner], dtype=float)}
                for owner in owner_profile.values[:, 1:]]
    
    # print(inputs)

    score = []
    for data in inputs:
      score.append(infer(**data)['dot_2'].numpy()[0, 0])

    return score, own_username


# Entar recommender berarti harus update semua data usernya tiap:
# 1. Ada owner baru (update score buat 1 owner ke semua influencer)
# 2. Ada influencer baru (update score buat semua owner ke 1 influencer)
# 3. Ada review baru (update score buat semua owner ke 1 influencer)


# print(get_owner_score_to_all_influencer("goto", inf_data, own_data))
# print()
# print(get_influencer_score_for_all_owner("acong69", inf_data, own_data))