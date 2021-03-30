import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("test/datasets/mushrooms.csv")

# drop veil-type column with 1 type
df1=df.drop(axis=1, labels = ['veil-type'])

df1["stalk-root"].replace({"?": None}, inplace = True)

# df with class column in the end
keys = list(df1.keys())
new_order = keys[1:]+[keys[0]]
df2 = df1[new_order]

cat = [0, 1, 2, 4, 8 , 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
bools = [3, 5, 6, 7, 9]

train, test = train_test_split(df2, test_size=0.2)
train_lbls = train['class']
test_lbls = test['class']
train_wo_lbls = train.drop(axis=1, labels = ['class'])
test_wo_lbls = test.drop(axis=1, labels = ['class'])

df2.to_csv("mushrooms_final.csv")

train.to_csv("train.csv")
test.to_csv("test.csv")

train_lbls.to_csv("train_lbls.csv")
test_lbls.to_csv("test_lbls.csv")

train_wo_lbls.to_csv("train_wo_lbls.csv")
test_wo_lbls.to_csv("test_wo_lbls.csv")