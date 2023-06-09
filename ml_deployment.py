import tensorflow as tf
import pandas as pd
# MODEL = "recommender-smote-try-simple-I"
# TODO: Nambahin username dari owner di setiap review

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
      "username": "acong69",
      "photo_profile_url": "https://nextluxury.com/wp-content/uploads/funny-profile-pictures-4.jpg",
      "ig_username": "acongig",
      "categories": [
        "mahasiswa",
        "perjaka"
      ],
      "yt_username": "acongyt",
      "password": "$2b$12$cU2FI4JaD0krjBhTlU5.UuHPya2Hc75ec5RCRPMqbFF0b/seleWr2",
      "ig_followers": 100,
      "reviews": [
        {
          "rating": 4,
          "comment": "wah tole jing",
          "order_id": "028df25c-2d9b-4ad9-9675-9b343645f45c",
          "company_name": "selulercapgo",
          "time_reviewed": "2023-06-09T19:30:11.358464+00:00"
        },
        {
          "rating": 2,
          "sentiment": 0.00046048188232816756,
          "comment": "jelek jing",
          "order_id": "faf23262-62ca-457b-a32c-62ebafe02962",
          "company_name": "selulercapgo",
          "time_reviewed": "2023-06-09T22:11:23.570854+00:00"
        }
      ],
      "userid": "fb5121b8-fd20-430d-b449-49dd718ede9e",
      "products": [
        {
          "social_media_type": "Instagram",
          "description": "uakak",
          "name": "Paket A",
          "to_do": [
            "nsksl"
          ],
          "product_id": 0,
          "price": 1902
        }
      ],
      "tt_username": "acongtt",
      "email": "aconkk@gmail.com",
      "address": "Jl. In Aja Dulu",
      "tt_followers": 5000,
      "yt_followers": 1000
    },
    {
      "tt_followers": 100000,
      "photo_profile_url": "https://nextluxury.com/wp-content/uploads/funny-profile-pictures-4.jpg",
      "ig_username": "bensim",
      "categories": [
        "Food and Drinks",
        "Technology",
        "Travel",
        "Gaming"
      ],
      "yt_username": "bensim",
      "password": "$2b$12$lzc8sZ60.KywPCE00ChCye/MXmwkEgquSfLq..FVIT/EaHQ3qnQPC",
      "ig_followers": 100000,
      "userid": "adfd58d7-380b-4b86-ad75-55380242c3ea",
      "products": [],
      "tt_username": "bensim",
      "email": "bensim2@gmail.com",
      "address": "wkwkwk",
      "username": "bensim",
      "yt_followers": 123400
    },
    {
      "tt_followers": 120000,
      "photo_profile_url": "",
      "ig_username": "iuu",
      "categories": [
        "Beauty and Fashion"
      ],
      "yt_username": "iuuu",
      "password": "$2b$12$/IlYcZ49uWvl0ixQf5buOOv63d/BRK2U1JWnZ.SkyOO4nRZAm1gWu",
      "ig_followers": 120000,
      "reviews": [
        {
          "rating": 4,
          "comment": "jelek jing",
          "order_id": "02a6c4eb-9db7-4a55-8f6c-5f9e8db0e034",
          "company_name": "Burjoni Sirojudin",
          "time_reviewed": "2023-06-09T15:04:17.978714+00:00"
        },
        {
          "rating": 4,
          "comment": "jelek jing",
          "company_name": "Burjoni Sirojudin",
          "time_reviewed": "2023-06-09T15:08:33.776231+00:00"
        }
      ],
      "userid": "b1779729-547f-403e-ba73-9870ebf80f50",
      "products": [
        {
          "social_media_type": "Youtube",
          "description": "hskanw",
          "name": "Paket Y",
          "to_do": [
            "bsksk"
          ],
          "product_id": 0,
          "price": 18000
        },
        {
          "social_media_type": "Youtube",
          "description": "jskamq",
          "name": "Paket L",
          "to_do": [
            "banaka"
          ],
          "product_id": 1,
          "price": 120202
        },
        {
          "social_media_type": "Instagram",
          "description": "jsksjsb",
          "name": "Paket A",
          "to_do": [
            "bskssls"
          ],
          "product_id": 2,
          "price": 1010
        }
      ],
      "tt_username": "iuu",
      "email": "iu@gmail.com",
      "address": "wkwkwkw",
      "username": "iuuu",
      "yt_followers": 12000
    }
  ]


own_data = [
    {
      "password": "$2b$12$mpeZFtoY6Ebvdl3A6hLwKOsMzT.A5kOFWnwJElaPBLbTSG9mk9WUm",
      "userid": "96d39401-1493-45f4-9817-a6657624f1ac",
      "email": "sipodang@gmail.com",
      "categories": [
        "Technology",
        "Lifestyle"
      ],
      "company_name": "Burjoni Sipodang",
      "username": "burjoni_s"
    },
    {
      "password": "$2b$12$KMXw6J.Oxc3VjO3s8Vobs.yK0C93ng5NUo/.OFAu/ztwKj4tLysma",
      "userid": "5749a971-3afa-43cb-b317-f94fda8ef3e4",
      "email": "sirojudin@gmail.com",
      "categories": [
        "Food and Drinks",
        "Entertainment"
      ],
      "company_name": "Burjoni Sirojudin",
      "username": "burjoni_sirojudin"
    },
    {
      "password": "$2b$12$cU7Kn6uu1NpP/TABddjna.pEqd7W61fE05Fvs2dwNjvorfDvqHI5C",
      "userid": "d0699a28-ed11-4755-a8f1-f703eabce04f",
      "email": "goto@gmail.com",
      "categories": [
        "Food and Drinks",
        "Sports",
        "Travel",
        "Gaming"
      ],
      "company_name": "gojek",
      "username": "goto"
    },
    {
      "password": "$2b$12$CxPdFdkpOqifS5AZWIHc2uiXMk.f5pURtX6miCThomYRz160fiKai",
      "userid": "0f098746-d29d-4b29-a83b-4e99890862c6",
      "email": "koma@gmail.com",
      "categories": [
        "Health"
      ],
      "company_name": "koma",
      "username": "koma spasi"
    },
    {
      "password": "$2b$12$RoNYKl0ba64XXLHnP0G.3efSbGzUx9vRpG/rnpyi34D113kcsAHdW",
      "userid": "2d156490-f1c1-4091-91a6-77eb52432613",
      "email": "kuebunga69@gmail.com",
      "categories": [
        "fnb",
        "umkm"
      ],
      "company_name": "kuebunga",
      "username": "kuebunga69"
    },
    {
      "password": "$2b$12$FuZX6XsS2/IhodaVXccLHOwbikFz0YgWlh0kPe.FuQplniOfMnEUG",
      "userid": "128ce810-87c8-4942-896e-d194a53e5155",
      "email": "seluler15@gmail.com",
      "categories": [
        "electronic",
        "hardware"
      ],
      "company_name": "selulercapgo",
      "username": "seluler15"
    },
    {
      "password": "$2b$12$1RM.cd/ZBsKX1/Hg7LP3Pu7kFUB1vqA38Acu8PYApSb5eZBR0gS6.",
      "userid": "c13f364d-99cd-4bf6-aa9a-e611c1c34eba",
      "email": "seluler18@gmail.com",
      "categories": [
        "electronic",
        "hardware"
      ],
      "company_name": "selulercappue",
      "username": "seluler18"
    },
    {
      "password": "$2b$12$KGHY4MERezWEhhfSSxpE4OjiW9iU0cxKg4ozZTkFCDQSLMGblCF3W",
      "userid": "5f3f4fae-5e4c-45ba-ac55-599a03914b1a",
      "email": "seluler69@gmail.com",
      "categories": [
        "electronic",
        "hardware"
      ],
      "company_name": "selulercappue",
      "username": "seluler69"
    },
    {
      "password": "$2b$12$Pce/G9LxVzKnXicWyTcKOurVTg1EE2dUnSmFOQDLjoLPHkpkPnqgG",
      "userid": "1466141d-1938-481c-b9dc-9db160c535bf",
      "email": "stark@gmail.com",
      "categories": [
        "Technology"
      ],
      "company_name": "stark",
      "username": "stark"
    },
    {
      "password": "$2b$12$7c1.TXUtqi.AQ7p51WVIHuVZyYge4PnNt32LGhdnlnbZe0hpbFmkS",
      "userid": "778186d3-189f-4513-aeee-a7df369a41fd",
      "email": "stark@gmail.com",
      "categories": [
        "Technology",
        "Gaming",
        "Entertainment"
      ],
      "company_name": "stark industry",
      "username": "stark_industry"
    }
  ]




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
    df_inf = pd.DataFrame(influencers).fillna(0)
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
    df_inf = df_inf.reindex(columns=['username'] + INF_PROFILE).fillna(0)

    return df_inf

# def get_all_owner_profile():

def get_combined_rating(rating, sentiment_rating):
    sentiment_rating = sentiment_rating.fillna(1)
    return STAR_WEIGHT * rating / 5 + SENTIMENT_WEIGHT * sentiment_rating

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
        features_except_categories = list(set(owner_profile.columns) - set(CATEGORIES))
        owner_profile[features_except_categories] = owner_profile[features_except_categories] / len(owner_reviews)
        owner_profile[CATEGORIES] = (owner_profile[CATEGORIES] + one_hot_categories) / (len(owner_reviews) + 1)
    else:
        owner_profile = one_hot_categories

    # Reorder columns
    owner_profile = owner_profile.filter(OWNER_PROFILE, axis=1)
    owner_profile['username'] = username
    owner_profile = owner_profile.reindex(columns=['username'] + OWNER_PROFILE).fillna(0)

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
    owner_reviews_count = owner_reviews.groupby("company_name").count()['inf_username']
    owner_reviews_count = owner_reviews_count.reindex(owners['company_name'].unique(), fill_value=0)
    df_inf = get_all_influencer_recommender_profile(influencers).drop('avg_rating', axis=1)

    # Multiply reviews with influencer's features
    owner_profiles = owner_reviews.merge(df_inf, left_on='inf_username', right_on='username')
    owner_profiles[OWNER_PROFILE] = owner_profiles[OWNER_PROFILE].mul(owner_profiles['combined_rating'], axis=0)
    owner_profiles = owner_profiles.drop(['username', 'inf_username', 'combined_rating'], axis=1)

    # Get mean of each features as user profile
    owner_profiles = owner_profiles.groupby('company_name').sum()
    features_except_categories = list(set(owner_profiles.columns) - set(CATEGORIES))
    owner_profiles[features_except_categories] = owner_profiles[features_except_categories].div(owner_reviews.groupby("company_name").count()['inf_username'], axis=0)
    owner_profiles = owner_profiles.combine_first(one_hot_categories).fillna(0)
    owner_profiles[CATEGORIES] = owner_profiles[CATEGORIES].div(owner_reviews_count + 1, axis=0)
   
    # Reorder columns
    owner_profiles = owner_profiles.filter(OWNER_PROFILE, axis=1)
    owner_profiles['company_name'] = owner_profiles.index
    owner_profiles = owner_profiles.reindex(columns=['company_name'] + OWNER_PROFILE).fillna(0)

    return owner_profiles

# get_all_owner_recommender_profile()

# Inference according to own_id
def get_owner_score_to_all_influencer(username, influencers, owners):
    # export_path = "recommender-model"
    # model = tf.saved_model.load(export_path)
    # infer = model.signatures["serving_default"]

    inf_profile = get_all_influencer_recommender_profile(influencers)
    owner_profile = get_owner_recommender_profile(username, influencers, owners)
    if (owner_profile == None):
        print("Owner not found")

    id = inf_profile['username']
    inputs = [{'inf_feature': tf.convert_to_tensor([inf], dtype=float), 
                'own_feature': tf.convert_to_tensor(owner_profile.values[:, 1:], dtype=float)}
                for inf in inf_profile.values[:, 1:]]

    print(inputs)

    # score = []
    # for i, data in enumerate(inputs):
    #     score.append(infer(**data))
    #     print(f"UserID: {own_id}, Inf ID: {int(id[i])} ->", infer(**data)['dot_2'].numpy()[0, 0])

def get_influencer_score_for_all_owner(username, influencers, owners):
    # export_path = "recommender-model"
    # model = tf.saved_model.load(export_path)
    # infer = model.signatures["serving_default"]

    inf_profile = get_influencer_recommender_profile(username, influencers)
    owner_profile = get_all_owner_recommender_profile(influencers, owners)    

    id = owner_profile['company_name'].values
    inputs = [{'inf_feature': tf.convert_to_tensor(inf_profile.values, dtype=float), 
                'own_feature': tf.convert_to_tensor([owner], dtype=float)}
                for owner in owner_profile.values[:, 1:]]
    
    # score = []
    # for i, data in enumerate(inputs):
    #     score.append(infer(**data))
    #     print(f"UserID: {int(id[i])}, Inf ID: {inf_id} ->", infer(**data)['dot_2'].numpy()[0, 0])


# Entar recommender berarti harus update semua data usernya tiap:
# 1. Ada owner baru (update score buat 1 owner ke semua influencer)
# 2. Ada influencer baru (update score buat semua owner ke 1 influencer)
# 3. Ada review baru (update score buat semua owner ke 1 influencer)


# get_owner_score_to_all_influencer("burjoni_sirojudin", inf_data, own_data)
# print()
get_influencer_score_for_all_owner("acong69", inf_data, own_data)