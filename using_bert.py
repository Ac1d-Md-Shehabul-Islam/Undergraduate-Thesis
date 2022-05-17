# -*- coding: utf-8 -*-
"""using_BERT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XUrYXPllgS2QfBLnGe66uZZwetIHY5EB
"""

import pandas as pd
import numpy as np

df = pd.read_csv("/content/drive/MyDrive/Thesis Papers/SMHD/final_cleaned_data.csv")

df["Label"].value_counts()

df_c = df[df["Label"] == "control"]
df_d = df[df["Label"] == "schizophrenia"]
df_c = df_c.sample(frac =1 )
df_c = df_c.sample(frac =1 ).iloc[0:1500,]
df_d = df_d.sample(frac =1 )
# df_d = df_d.sample(frac =1 ).iloc[0:5000,]

def stripstr(x):
   return len(x.strip())==0

result = pd.concat([df_c, df_d], ignore_index=True, sort=False)

empty = result[result["Posts"].apply(stripstr)]

indexarr = empty.index
result.drop(index = indexarr, inplace=True)

result = result.sample(frac = 1)

# def cut(sen, length = 1000):
#   content = sen.split()
#   if len(content) < length:
#     return " ".join(content)
#   return " ".join(content[0:length])

# x=newdf['Posts'].apply(cut)

result["Label"].value_counts()

x=result["Posts"]
y=result["Label"]

y=result["Label"]

y = np.array(list(map(lambda x: 1 if x=="schizophrenia" else 0, y)))

"""# bert"""

!pip install bert-for-tf2
!pip install sentencepiece

# Commented out IPython magic to ensure Python compatibility.
try:
#   %tensorflow_version 2.x
except Exception:
  pass
import tensorflow as tf

import tensorflow_hub as hub

from tensorflow.keras import layers
import bert

BertTokenizer = bert.bert_tokenization.FullTokenizer
bert_layer = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/1", trainable=False)
vocabulary_file = bert_layer.resolved_object.vocab_file.asset_path.numpy()
to_lower_case = bert_layer.resolved_object.do_lower_case.numpy()
tokenizer = BertTokenizer(vocabulary_file, to_lower_case)

def tokenize_reviews(text_reviews):
  return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(text_reviews))

tokenized_reviews = [tokenize_reviews(review) for review in reviews]

type(tokenized_reviews[0])

reviews_with_len = []
i=0
for  review in tokenized_reviews:
  reviews_with_len.append([review, y[i], len(review)])
  i=i+1

reviews_with_len.sort(key=lambda x: x[2])

sorted_reviews_labels = [(review_lab[0], review_lab[1]) for review_lab in reviews_with_len]

processed_dataset = tf.data.Dataset.from_generator(lambda: sorted_reviews_labels, output_types=(tf.int32, tf.int32))

BATCH_SIZE = 32
batched_dataset = processed_dataset.padded_batch(BATCH_SIZE, padded_shapes=((None, ), ()))

next(iter(batched_dataset))

import math

TOTAL_BATCHES = math.ceil(len(sorted_reviews_labels) / BATCH_SIZE)
TEST_BATCHES = TOTAL_BATCHES // 10
batched_dataset.shuffle(TOTAL_BATCHES)
test_data = batched_dataset.take(TEST_BATCHES)
train_data = batched_dataset.skip(TEST_BATCHES)

class TEXT_MODEL(tf.keras.Model):
    
  def __init__(self,vocabulary_size,embedding_dimensions=128,cnn_filters=50, dnn_units=512, model_output_classes=2, dropout_rate=0.1, training=False,name="text_model"):
    super(TEXT_MODEL, self).__init__(name=name)
    
    self.embedding = layers.Embedding(vocabulary_size,embedding_dimensions)
    self.cnn_layer1 = layers.Conv1D(filters=cnn_filters,kernel_size=2,padding="valid",activation="relu")
    self.cnn_layer2 = layers.Conv1D(filters=cnn_filters,kernel_size=3,padding="valid",activation="relu")
    self.cnn_layer3 = layers.Conv1D(filters=cnn_filters,kernel_size=4,padding="valid",activation="relu")
    self.pool = layers.GlobalMaxPool1D()
    
    self.dense_1 = layers.Dense(units=dnn_units, activation="relu")
    self.dropout = layers.Dropout(rate=dropout_rate)
    if model_output_classes == 2:
      self.last_dense = layers.Dense(units=1, activation="sigmoid")
    else:
      self.last_dense = layers.Dense(units=model_output_classes, activation="softmax")
    
  def call(self, inputs, training):
    l = self.embedding(inputs)
    l_1 = self.cnn_layer1(l) 
    l_1 = self.pool(l_1) 
    l_2 = self.cnn_layer2(l) 
    l_2 = self.pool(l_2)
    l_3 = self.cnn_layer3(l)
    l_3 = self.pool(l_3) 
    
    concatenated = tf.concat([l_1, l_2, l_3], axis=-1) # (batch_size, 3 * cnn_filters)
    concatenated = self.dense_1(concatenated)
    concatenated = self.dropout(concatenated, training)
    model_output = self.last_dense(concatenated)
    
    return model_output

VOCAB_LENGTH = len(tokenizer.vocab)
EMB_DIM = 200
CNN_FILTERS = 100
DNN_UNITS = 256
OUTPUT_CLASSES = 2

DROPOUT_RATE = 0.2

NB_EPOCHS = 5

text_model = TEXT_MODEL(vocabulary_size=VOCAB_LENGTH,
                        embedding_dimensions=EMB_DIM,
                        cnn_filters=CNN_FILTERS,
                        dnn_units=DNN_UNITS,
                        model_output_classes=OUTPUT_CLASSES,
                        dropout_rate=DROPOUT_RATE)

if OUTPUT_CLASSES == 2:
  text_model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
else:
  text_model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["sparse_categorical_accuracy"])

text_model.fit(train_data, epochs=NB_EPOCHS)