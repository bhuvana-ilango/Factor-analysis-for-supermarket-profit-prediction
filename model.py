# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import sklearn 

train = pd.read_csv('Train.csv')
test = pd.read_csv('Test.csv')

data=train.append(test)

categorical_columns=[x for x in data.dtypes.index if data.dtypes[x]=='object']

categorical_columns=[x for x in categorical_columns if x not in ['Item_Identifier','Outlet_Identifier']] 

data.Item_Weight.fillna(data.Item_Weight.mean(),inplace=True)

mode = data['Outlet_Size'].mode()[0]

# Fill the missing values with the mode
data['Outlet_Size'].fillna(mode, inplace=True)

data.loc[data['Item_Visibility']==0,'Item_Visibility']=data.Item_Visibility.mean()

data['Item_Type_Combined']=data.Item_Identifier.apply(lambda x:x[0:2])

data['Item_Type_Combined']=data.Item_Type_Combined.map({'FD':'Food and Drinks','NC':'Non-Consumable','DR':'Drinks'})

data['Outlet_Years']=2013-data['Outlet_Establishment_Year']

data.Item_Fat_Content=data.Item_Fat_Content.replace({'LF':'Low Fat','reg':'Regular','low fat':'Low Fat'})

data.loc[data['Item_Type_Combined']=='Non-Consumable','Item_Fat_Content']='Non-Edible'

data.drop(['Outlet_Establishment_Year','Item_Type'],inplace=True,axis=1)

Item_Sales=data.Item_Outlet_Sales

train=data.iloc[:8523,:]

test=data.iloc[8523:,:]

test.drop('Item_Outlet_Sales',inplace=True,axis=1)

# A generalization function to prediction and file on sharing
target='Item_Outlet_Sales'
IDcol=['Item_Identifier','Outlet_Identifier']
from sklearn import model_selection ,metrics
def modelfit(alg,dtrain,dtest,predictor,target,IDcol,filename):
    alg.fit(dtrain[predictor],dtrain[target])
    prediction=alg.predict(dtrain[predictor])
    #now cross_validation
    cv_score=model_selection.cross_val_score(alg,dtrain[predictor],dtrain[target],cv=20,scoring='neg_mean_squared_error')
    cv_score=np.sqrt(np.abs(cv_score))
    print(np.sqrt(metrics.mean_squared_error(dtrain[target].values,prediction)))
    print("CV_SCORE : mean - %.4g | std - %.4g | max - %.4g | min - %.4g" % (np.mean(cv_score),np.std(cv_score),np.max(cv_score),np.min(cv_score)))
    dtest[target]=alg.predict(dtest[predictor])

    #now export on submission file
    IDcol.append(target)
    submission=pd.DataFrame({x:dtest[x] for x in IDcol})
    submission.to_csv(f'{filename}',index=False)

#Linear Regression on training set
from sklearn.linear_model import LinearRegression , Ridge,Lasso
predictor=[x for x in train.columns if x not in [target]+IDcol]
alg1=LinearRegression()
alg1.fit(train[predictor], train[target])
prediction = alg1.predict(train[predictor])
# modelfit(alg1,train,test,predictor,target,IDcol,'alg1.csv')

import pickle
# # Saving model to disk
pickle.dump(alg1, open('model.pkl','wb'))
model=pickle.load(open('model.pkl','rb'))
print(prediction)