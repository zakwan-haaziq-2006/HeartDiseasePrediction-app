import pandas as pd
import numpy as np

df = pd.read_csv('hearts.csv')
print(df)

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()

df['Sex'] = le.fit_transform(df['Sex'])
df['ChestPainType'] = le.fit_transform(df['ChestPainType'])
df['RestingECG'] = le.fit_transform(df['RestingECG'])
df['ExerciseAngina'] = le.fit_transform(df['ExerciseAngina'])
df['ST_Slope'] = le.fit_transform(df['ST_Slope'])

#rint(df)
print(df.value_counts())

X = df.drop(columns='HeartDisease')
Y = df['HeartDisease']

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size=0.2,random_state=10)

from sklearn.naive_bayes import GaussianNB
Nb = GaussianNB()

print("Training model...")
Nb.fit(x_train,y_train)
print("Model trained....")

y_predict = Nb.predict(x_test)

from sklearn.metrics import accuracy_score
print("Accuracy :",accuracy_score(y_pred=y_predict,y_true=y_test))

y = [[40,1,1,140,289,0,1,172,0,0.0,2]]
pred = Nb.predict(y)
print(pred)

import pickle
pickle.dump(Nb,open("Model.pkl",'wb'))
