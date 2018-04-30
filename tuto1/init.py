# Common imports
import numpy as np
import os
import pandas as pd

#housing = load_housing_data()
housing = pd.read_csv("datasets/housing/housing.csv")

print("Head")
print(housing.head())

print("Infos")
housing.info()

print("ocean_proximity")
housing["ocean_proximity"].value_counts()
print(housing["ocean_proximity"].value_counts())

print(housing.describe())

import matplotlib.pyplot as plt
housing.hist(bins=50, figsize=(20,15))
plt.show()