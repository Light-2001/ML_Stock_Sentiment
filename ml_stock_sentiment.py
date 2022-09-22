# -*- coding: utf-8 -*-
"""ML_Stock_Sentiment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V5r0esPA5unuAG-YjHPrEDccAJAkFZl8

# Predicting stock Movement based on sentiment analysis

## Ritesh Pandey 2019132
## Rishabh Saxena 2019129


Our project is aimed to find correlation between the stock market trend and the sentiment trend on twitter for a company and its corresponding impact on the stock trend for a company

## Overall Methodology



The summary can be understood from the below flowchart
"""

# Commented out IPython magic to ensure Python compatibility.
# %pylab inline
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.pyplot import figure

figure(figsize=(15 ,20), dpi=80)
img = mpimg.imread('flowcharts/overall.png')

imgplot = plt.imshow(img)
plt.show()

"""## Collecting tweets for about a month 

### Twitter data was fetched from Tweepy library. Due to Twitter limitations one can only fetch  tweets upto 7 days-tweet-archive, therefore we periodically(7-day window) collected data over the last month(March-2022->April-2022) which were related to Microsoft.

#### The below mentioned code is just an explanation for getting tweets from twitter. For our project we collected data regulary. The final tweets dataset could be found with other files
"""

import tweepy


# your Twitter API key and API secret
my_api_key = "UaDnqHls8aFIls5dCB2mTZIkm"
my_api_secret = "2nUbfrhMNsBguN0knYuLhabQpHocS6HB90yu0boBknW6jYqq0P"
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAO1IaQEAAAAA0wAvlYLm9YfIGbkp9KBsyk57sUg%3D0pMuZggevJw6f9yeI16j9qSgT2BTYdQpPetDkYREL6FKGRLzIs'
access_token = '1292693670936813570-8uk1i0v9WlWgojuCFvjmWnnuoybdB3'
secret_access_token = 'J3D2B7BV3BzW0qoiE0yJlqEvbTr0oyPinzPabQSWihMZW'
# authenticate
auth = tweepy.OAuthHandler(my_api_key, my_api_secret)
auth.set_access_token(access_token, secret_access_token)
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token = bearer_token)

query = "microsoft"

response = client.search_recent_tweets(query=query, tweet_fields=['created_at','public_metrics', 'lang'], max_results=50)

"""## Get stock data for Microsoft(MSFT)

### The Microsoft stock data was fetched from the Yahoo library yfinance

## Our stock data collection is very different from the one which are used. Usually stock analysis is performed on per day basis

## We explored further for microanalysis, and retrieved data for 15 minute period, this could be understood with the below diagram.

###  For each day the stock market is active for 6hrs  and for each hour we have 4 fifteen minute intervals, which implies that for each day we have 6x4 = 24 Entries
"""

figure(figsize=(15 ,20), dpi=80)
img = mpimg.imread('flowcharts/stock-data-collection.png')

imgplot = plt.imshow(img)
plt.show()

import pandas as pd

import numpy as np

import yfinance as yf
import matplotlib.pyplot as plt
import seaborn

data_stock_microsoft = yf.download("MSFT", start="2022-03-25", end="2022-04-14", interval='15M')

data_stock_microsoft.index

df_microsoft = pd.DataFrame(data_stock_microsoft)

#check for na or missing values
df_microsoft.isna().sum()

df_microsoft.tail()

df_microsoft['up_or_down'] = df_microsoft.Close - df_microsoft.Open

df_microsoft['bullish_or_bearish'] = np.where(df_microsoft['up_or_down']>=0,1,-1)

df_microsoft.describe()

"""## Changing the timezone of the stock data as the tweets are as of IST timezone

### the stock data was of Eastern time zone
"""

temp = df_microsoft.tz_convert('Asia/Kolkata')

df_microsoft = temp

df_microsoft.shape

"""## Preprocess tweet data


### The tweets collected contained many attributes like tweet_id, user_id etc. We only kept the attributes relevant to our project like { date, time, tweet, retweet count, like count , language}

"""

#load dataset
import json
cols = ['date', 'time' , 'tweet','retweets_count','likes_count','language']
data = []
file_name = 'MSFT_final_uncleaned.json'

with open(file_name, encoding='latin-1') as f:
    for line in f:
        
        try:
            doc = json.loads(line)
            lst = [doc['date'], doc['time'],doc['tweet'],doc['retweets_count'],doc['likes_count'],doc['language']]
            data.append(lst)
        except:
            break

df_tweets = pd.DataFrame(data=data, columns=cols)

df_tweets.shape

"""### Keep only english language tweets

#### The tweets were collected from a global source because of which there were tweets in other languages as well
"""

index_not_english_tweets = df_tweets[ (df_tweets['language'] != 'en') ].index
df_tweets.drop(index_not_english_tweets, inplace = True)

df_tweets.head(10)

#after keeping only english language tweets
df_tweets.shape

df_tweets.isna().sum()

"""## Cleaning Tweet data 
### No cleaning/preprocessing(like stemming, tokenization, lemmatization) required for vader sentiment analysis


## VADER : Valence Aware Dictionary & Sentiment Reasoner
### A lexicon and rule based sentiment analyser, works well on Social data like tweets
### Considers emojis and shorthand  acronymns like LOL/ROFL etc while calculating sentiment score.

### For a given input text VADER model gives it a positive score, neutral score, negative score & compound score. The magnitude of the score defines how strong the respective sentiment is in the given input

## Perform VADER sentiment analysis
"""

# Commented out IPython magic to ensure Python compatibility.

import nltk 
import string
import re
# %matplotlib inline

df_tweets.isna().sum()

"""## Give sentiment score to each tweet"""

import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import unicodedata

sentiment_i_a = SentimentIntensityAnalyzer()
for indexx, row in df_tweets.T.iteritems():
    try:
        sentence_i = unicodedata.normalize('NFKD', df_tweets.loc[indexx, 'tweet'])
        sentence_sentiment = sentiment_i_a.polarity_scores(sentence_i)
        df_tweets.at[indexx,'Comp']=sentence_sentiment['compound']
        df_tweets.at[indexx,'Negative']=sentence_sentiment['neg']
        df_tweets.at[indexx,'Neutral']=sentence_sentiment['neu']
        df_tweets.at[indexx,'Positive']=sentence_sentiment['pos']
        
    except TypeError:
        #print (stocks_dataf.loc[indexx, 'Tweets'])
        print (indexx)

"""## Defining the importance of a tweet sentiment based on likes and retweets

### It is widely observed that if an eminent personality tweets positively about some company and it recieves good response in terms of likes and re-tweets; then the stock price of the company is obsereved to go up. Hence we have given a tweet sentiment more importance if that tweets has higher likes and retweets compared to another tweet.

### This is also a novelty of our project, as for all the research or projects in tweet sentiment analysis for stock data we came across in literature survey, they have not given preference to a particular tweet sentiment based on any metric



#### We have given a buffer like count and retweet count of 1 to each tweet so that tweets with 0 likes or 0 retweets is not discarded by the model
"""

df_tweets['retweets_count'] = df_tweets['retweets_count']+1
df_tweets['likes_count'] = df_tweets['likes_count']+1

df_tweets.head()

"""## Finding the sentiment trend during a 15 min interval for a stock entry( MSFT)

## We find the tweets posted during that time period and try to find a cumulative sentiment score

### for a entry in the stock data, we 
    #1 find the tweets posted in the given time along with the individual sentiment score
    #2 for each tweet find the harmonic mean of the retweet count and like count to define importance of the tweet sentiment and multiply it with the respective sentiment score individualy(positive/negative/neutral/compound)
    #3 sum all the respective scores and normalize. Now we have the overal sentiment during the 15 minute interval
        
"""

figure(figsize=(15 ,20), dpi=80)
img = mpimg.imread('flowcharts/overall-sentiment-for-stock-entry.png')

imgplot = plt.imshow(img)
plt.show()

df_microsoft['Positive'] = 0
df_microsoft['Positive'].astype(float)

df_microsoft['Negative'] = 0
df_microsoft['Negative'].astype(float)

df_microsoft['Neutral'] = 0
df_microsoft['Neutral'].astype(float)

df_microsoft['Compound'] = 0
df_microsoft['Compound'].astype(float)

df_microsoft['Total_Tweets'] = 0
df_microsoft['Total_Tweets'].astype(float)

df_microsoft

import datetime
def getRelatedTweets(dates, time_start,time_end):
    time_start = datetime.datetime.strptime(time_start, '%H:%M:%S')
    time_end = datetime.datetime.strptime(time_end, '%H:%M:%S')
    
        
    #print(time_start)
    #print(time_end)
    #print(dates)
    df_filtered_date = df_tweets.query('date == @dates')
    final_list = []
    if len(df_filtered_date) == 0:
        return []
    for ind, entry in df_filtered_date.iterrows():
        
        #print(entry.time)
        time_tweet = datetime.datetime.strptime(entry.time, '%H:%M:%S')
        #print(time_tweet)
        if(time_end == '00:00:00'):
            if time_tweet>time_start:
                final_list.append(entry)
                continue
        if time_tweet < time_end and time_tweet>time_start:
            #print(time_tweet)
            final_list.append(entry)
            
            
    return final_list
    #for tweet in final_list:

def performExperiment():
    #df_microsoft['sentiment'] = 0
    #df_microsoft['sentiment'].astype(float)
    count_no_tweet=0      
    for pos,index_date in enumerate(df_microsoft.index):
        #print("date : ",str(index_date)[:10])
        #print("time start :",str(index_date)[11:19])
        time_start = str(index_date)[11:19]
        hr,mins, sec = time_start.split(':')

        mins = 15 + int(mins)
        if mins==60:
            mins = '00'
            hr = str((int(hr)+1)%24)
        mins=str(mins)
        time_end = ':'.join([hr,mins,sec])
        #print("time end :",time_end)
        dates = str(index_date)[:10]

        related_tweets = getRelatedTweets(dates, time_start,time_end)

        if len(related_tweets)!=0:
            sentiment_positive = []
            sentiment_negative = []
            sentiment_compound = []
            sentiment_neutral = []
            
            count = 0
            for each_Tweet in related_tweets:

                harmonic_mean_of_like_and_retweet = 2*each_Tweet['likes_count']*each_Tweet['retweets_count']/(each_Tweet['likes_count'] + each_Tweet['retweets_count'])
                
                count+=each_Tweet['likes_count']
                #sentiments.append(score)
                sentiment_positive.append(each_Tweet['Positive']*harmonic_mean_of_like_and_retweet)
                sentiment_negative.append(each_Tweet['Negative']*harmonic_mean_of_like_and_retweet)
                sentiment_compound.append(each_Tweet['Comp']*harmonic_mean_of_like_and_retweet)
                sentiment_neutral.append(each_Tweet['Neutral']*harmonic_mean_of_like_and_retweet)
            #normalize
            sentiment_positive = [each/count for each in sentiment_positive]
            sentiment_negative = [each/count for each in sentiment_negative]
            sentiment_compound = [each/count for each in sentiment_compound]
            sentiment_neutral = [each/count for each in sentiment_neutral]
            #final_score = sum(sentiments)
            
            
            df_microsoft.iloc[pos,-5] = sum(sentiment_positive)
            df_microsoft.iloc[pos,-4] = sum(sentiment_negative)
            df_microsoft.iloc[pos,-3] = sum(sentiment_neutral)
            df_microsoft.iloc[pos,-2] = sum(sentiment_compound)
            df_microsoft.iloc[pos,-1] = len(sentiment_compound)

performExperiment()

#normalised scores
df_microsoft

"""## Adjusting for stock data entries where no tweets could be retrieved

### Some stock entries do not have any tweet during that 15 minute period( due to human error in the tweet collection process). We have replaced those values with the average value of respective sentiment score.
"""

temp1 = df_microsoft.copy(deep=False)
temp2 = df_microsoft[df_microsoft['Total_Tweets']!=0.0].copy(deep=False)
for pos,index_date in enumerate(temp1.index):
    #find bullish_or_bearish
    #for the type replace Postivie ..... Total TWEETS with avg
    stock_trend = temp1.iloc[pos,-6]
    #print(stock_trend)
    #print(temp1.iloc[pos,-1])
    if temp1.iloc[pos,-1]!=0:
        #print("-",pos)
        continue
    
    temp1.iloc[pos,-5] = np.mean(temp2[temp2['bullish_or_bearish']==stock_trend]['Positive'])
    temp1.iloc[pos,-4] = np.mean(temp2[temp2['bullish_or_bearish']==stock_trend]['Negative'])
    temp1.iloc[pos,-3] = np.mean(temp2[temp2['bullish_or_bearish']==stock_trend]['Neutral'])
    temp1.iloc[pos,-2] = np.mean(temp2[temp2['bullish_or_bearish']==stock_trend]['Compound'])
    temp1.iloc[pos,-1] = int(np.mean(temp2[temp2['bullish_or_bearish']==stock_trend]['Total_Tweets']))
    #if temp1.iloc[pos,-1]==0:
        #print('-----------')
        #print(pos)

temp_df = df_microsoft[df_microsoft['Total_Tweets']==0.0].copy(deep=False)
temp_df.shape

df_microsoft = temp1
temp_df = df_microsoft
temp_df.shape

"""## Finding correlation between sentiment and stock movement

"""

matrix = df_microsoft.corr()
print("Correlation matrix is : ")
print(matrix)

"""## Building ML MODEL"""

df_microsoft['gain_or_loss'] = df_microsoft['bullish_or_bearish']

#ARRANGING DATASET APPROPRIATELY


dataset_for_ML = df_microsoft.copy(deep=False)

dataset_for_ML.drop(['Open','High','Low','Close','Adj Close','bullish_or_bearish','Volume','up_or_down'],axis=1,inplace=True)

import pandas as pd
dataset_for_ML = pd.read_csv('Dataset for ML')

dataset_for_ML

X = dataset_for_ML.iloc[:, 1:-1].values
y = dataset_for_ML.iloc[:, -1].values

"""## Splitting for train and test"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 0)

"""## Feature scaling"""

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

X_train

model_evaluation_dictionary={}

"""## Preparing model Logistic Regression model"""

from sklearn.linear_model import LogisticRegression
classifier = LogisticRegression(random_state = 0,solver = 'saga',penalty = 'l2',class_weight = 'balanced',warm_start=True)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)

print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['Logistic'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

"""## Preparing decision tree model"""

from sklearn.tree import DecisionTreeClassifier
classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0,splitter = 'best')
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)

print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['DecisionTree'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

"""## Random Forest(Ensemble Learning)"""

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 0)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)

print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['RandomForest'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

"""## SVM"""

from sklearn.svm import SVC
classifier = SVC(kernel = 'rbf', C=1,random_state = 0, gamma='scale',coef0=-0.2,shrinking=False)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)

print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['SVM'] ={'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

"""## Naive Bayes"""

from sklearn.naive_bayes import GaussianNB
classifier = GaussianNB()
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)

print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['NaiveBayes'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

"""## KNN"""

from sklearn.neighbors import KNeighborsClassifier
classifier = KNeighborsClassifier(n_neighbors = 8, metric = 'minkowski', p = 3,weights='distance',algorithm='ball_tree')
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)
#print(cm)
print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['KNN'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

"""## Gradient Boosting"""

from sklearn.ensemble import GradientBoostingClassifier
classifier = GradientBoostingClassifier(n_estimators = 10, loss = 'exponential',subsample=1, criterion = 'mae',\
                                        max_features='sqrt',random_state = 0)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)

print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['GradientBoost'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

df_model_evaluation = pd.DataFrame(model_evaluation_dictionary)

df_model_evaluation

df_model_evaluation.to_csv('Model Evaluation for ML')

dataset_for_ML.to_csv('Dataset for ML')

"""## Exploring correlation between features to perform feature reduction using PCA"""

dataset_for_ML

matrix = dataset_for_ML.corr()
print("Correlation matrix is : ")
print(matrix)

"""## Dimension Reduction PCA

### We reduce the number of features from 5 to 2
"""

from sklearn.decomposition import PCA
pca = PCA(n_components = 2)
X_train = pca.fit_transform(X_train)
X_test = pca.transform(X_test)

"""## LOGISTIC"""

from sklearn.linear_model import LogisticRegression
classifier = LogisticRegression(random_state = 0,solver = 'saga',penalty = 'l2',class_weight = 'balanced',warm_start=True)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)
print(cm)
print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['PCA-Logistic'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

from matplotlib.colors import ListedColormap
X_set, y_set = X_train, y_train
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green', 'blue')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
plt.title('Logistic Regression (Training set)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()

from matplotlib.colors import ListedColormap
X_set, y_set = X_test, y_test
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green', 'blue')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
plt.title('Logistic Regression (Test set)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()

"""## Cross Validation K-fold for Logistic Regression"""

from sklearn.model_selection import cross_val_score
accuracies = cross_val_score(estimator = classifier, X = X_train, y = y_train, cv = 10)
print("Accuracy: {:.2f} %".format(accuracies.mean()*100))
print("Standard Deviation: {:.2f} %".format(accuracies.std()*100))

"""## Decision Tree"""

from sklearn.tree import DecisionTreeClassifier
classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0,splitter = 'best')
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)
print(cm)
print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['PCA-DT'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

X_set, y_set = X_train, y_train
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green', 'blue')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
plt.title('Decision Tree (Training set)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()

X_set, y_set = X_test, y_test
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green', 'blue')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
plt.title('Decision Tree (Test set)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()

"""## Cross Validation - K-fold for Decision Tree PCA"""

from sklearn.model_selection import cross_val_score
accuracies = cross_val_score(estimator = classifier, X = X_train, y = y_train, cv = 10)
print("Accuracy: {:.2f} %".format(accuracies.mean()*100))
print("Standard Deviation: {:.2f} %".format(accuracies.std()*100))

"""## KNN"""

from sklearn.neighbors import KNeighborsClassifier
classifier = KNeighborsClassifier(n_neighbors = 8, metric = 'minkowski', p = 3,weights='distance',algorithm='ball_tree')
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))
from sklearn.metrics import confusion_matrix, accuracy_score,precision_score, recall_score,f1_score
cm = confusion_matrix(y_test, y_pred)
print(cm)
print('accuracy :',accuracy_score(y_test, y_pred))
print('precision :',precision_score(y_test, y_pred))
print('recall :',recall_score(y_test, y_pred))
print('f1 :',f1_score(y_test, y_pred))
model_evaluation_dictionary['PCA-KNN'] = {'accuracy':accuracy_score(y_test, y_pred),'precision':precision_score(y_test, y_pred),'recall':recall_score(y_test, y_pred),'f1':f1_score(y_test, y_pred)}

X_set, y_set = X_train, y_train
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green', 'blue')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
plt.title('KNN (Training set)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()

X_set, y_set = X_test, y_test
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green', 'blue')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1],
                c = ListedColormap(('red', 'green', 'blue'))(i), label = j)
plt.title('KNN (Test set)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()

"""## Cross Validation - K-fold for KNN"""

from sklearn.model_selection import cross_val_score
accuracies = cross_val_score(estimator = classifier, X = X_train, y = y_train, cv = 10)
print("Accuracy: {:.2f} %".format(accuracies.mean()*100))
print("Standard Deviation: {:.2f} %".format(accuracies.std()*100))

pd.DataFrame(model_evaluation_dictionary)