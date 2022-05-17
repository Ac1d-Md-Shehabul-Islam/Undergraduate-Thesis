# -*- coding: utf-8 -*-
"""Cleanest_with_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RfgSWh_1EP0pp63yRp_d_VaS0WQPVfq5
"""

pip install ijson

from google.colab import drive
drive.mount('/content/drive')

# def check(val):
#   return (val=='depression' or val=='ptsd' or val=='schizophrenia' or val=='bipolar')

import pandas as pd
# import collections
# import ijson
#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfTransformer

# posts=[]
# labels=[]
# #c=0
# with open("/content/drive/MyDrive/Thesis Papers/SMHD/train.jl", "rb") as f:
#   for line in f:
#     # c=c+1
#     # if(c==20):
#     #   break
#     item = ijson.items(line,'posts.item.text',multiple_values=True)
    
#     label = ijson.items(line,'label',multiple_values=True)
#     for j in label:
#       if(len(j)==2):
#         for val in j:
#           if(check(val)):
#             labels.append(val)
#             s=""
#             space=" "
#             for i in item:
#               s=s+space+i
#             posts.append(s)
#       else:
#         if(check(j[0])):
#           labels.append(j[0])
#           s=""
#           space=" "
#           for i in item:
#             s=s+space+i
#           posts.append(s)

# df = pd.DataFrame({"Label": labels,"Posts": posts})

# df.head(10)

df = pd.read_csv('/content/drive/MyDrive/Thesis Papers/SMHD/train_less.csv')

df["Label"].value_counts()

"""**Logistic regression Start:**
It goes out of memory!!
"""

def _reciprocal_rank(true_labels: list, machine_preds: list):
  tp_pos_list = [(idx + 1) for idx, r in enumerate(machine_preds) if r in true_labels]

  rr = 0
  if len(tp_pos_list) > 0:

    first_pos_list = tp_pos_list[0]
        
        # rr = 1/rank
    rr = 1 / float(first_pos_list)

  return rr


def compute_mrr_at_k(items:list):
  rr_total = 0
    
  for item in items:   
    rr_at_k = _reciprocal_rank(item[0],item[1])
    rr_total = rr_total + rr_at_k
    mrr = rr_total / 1/float(len(items))

  return mrr

def collect_preds(Y_test,Y_preds):
    
  pred_gold_list=[[[Y_test[idx]],pred] for idx,pred in enumerate(Y_preds)]
  return pred_gold_list
             
def compute_accuracy(eval_items:list):
  correct=0
  total=0
    
  for item in eval_items:
    true_pred=item[0]
    machine_pred=set(item[1])
        
    for cat in true_pred:
      if cat in machine_pred:
        correct+=1
        break
    
    
  accuracy=correct/float(len(eval_items))
  return accuracy

from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn import metrics
import numpy as np

def extract_features(df,field,training_data,testing_data):
  # TF-IDF BASED FEATURE REPRESENTATION
  tfidf_vectorizer=TfidfVectorizer(use_idf=True, max_df=0.95)
  tfidf_vectorizer.fit_transform(training_data[field].values)
        
  train_feature_set=tfidf_vectorizer.transform(training_data[field].values)
  test_feature_set=tfidf_vectorizer.transform(testing_data[field].values)
        
  return train_feature_set,test_feature_set,tfidf_vectorizer

def get_top_k_predictions(model,X_test,k):
    
    # get probabilities instead of predicted labels, since we want to collect top 3
  probs = model.predict_proba(X_test)

    # GET TOP K PREDICTIONS BY PROB - note these are just index
  best_n = np.argsort(probs, axis=1)[:,-k:]
    
    # GET CATEGORY OF PREDICTIONS
  preds=[[model.classes_[predicted_cat] for predicted_cat in prediction] for prediction in best_n]
    
  preds=[ item[::-1] for item in preds]
    
  return preds
   
    
def train_model(df,field="text_desc",feature_rep="binary",top_k=3):
    
    
    
    # GET A TRAIN TEST SPLIT (set seed for consistent results)
  training_data, testing_data = train_test_split(df,random_state = 2000,)

    # GET LABELS
  Y_train=training_data['Label'].values
  Y_test=testing_data['Label'].values
     
    # GET FEATURES
  X_train,X_test,feature_transformer=extract_features(df,field,training_data,testing_data)

    # INIT LOGISTIC REGRESSION CLASSIFIER
  scikit_log_reg = LogisticRegression(verbose=1, solver='liblinear',random_state=0, C=5, penalty='l2',max_iter=1000)
  model=scikit_log_reg.fit(X_train,Y_train)
  
  predictions = model.predict(X_test)

    # GET TOP K PREDICTIONS
  preds=get_top_k_predictions(model,X_test,top_k)

    
    # GET PREDICTED VALUES AND GROUND TRUTH INTO A LIST OF LISTS - for ease of evaluation
  eval_items=collect_preds(Y_test,preds)
  conf = metrics.classification_report(Y_test,predictions) 
  conf_matrix = metrics.confusion_matrix(Y_test,predictions) 
    # GET EVALUATION NUMBERS ON TEST SET -- HOW DID WE DO?
  
  accuracy=compute_accuracy(eval_items)
  mrr_at_k=compute_mrr_at_k(eval_items)
  
    
  return model,feature_transformer,accuracy,mrr_at_k,conf,conf_matrix

field='Posts'
feature_rep='tfidf'
top_k=4

model,transformer,accuracy,mrr_at_k,confusion,m=train_model(df,field=field,feature_rep=feature_rep,top_k=top_k)

print("\nAccuracy={0}; MRR={1}".format(accuracy,mrr_at_k))
print(confusion)
print(m)



filter1=df["Label"].isin(["bipolar","depression"])
newdf=df[filter1]

y.map({'bipolar': 0, 'depression': 1})

def preprocess_text(sen):
  # Removing html tags
  sentence = remove_tags(sen)

  # Remove punctuations and numbers
  sentence = re.sub('[^a-zA-Z]', ' ', sentence)

  # Single character removal
  sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)

  # Removing multiple spaces
  sentence = re.sub(r'\s+', ' ', sentence)

  return sentence

import re

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
  return TAG_RE.sub('', text)

reviews = []
sentences = list(newdf['Posts'])
for sen in sentences:
  reviews.append(preprocess_text(sen))

from sklearn.model_selection import train_test_split

x=reviews
y=newdf["Label"]

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.3,random_state=42)

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', MultinomialNB()),])
text_clf = text_clf.fit(x_train, y_train)

# del labels
# del posts

predictions = text_clf.predict(x_test)

from sklearn import metrics

print(metrics.confusion_matrix(y_test,predictions))

print(metrics.classification_report(y_test,predictions))

print(metrics.accuracy_score(y_test,predictions))