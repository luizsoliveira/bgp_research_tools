from sklearn.ensemble import ExtraTreesClassifier
import os
import pandas as pd
import numpy as np
from dataset.dataset import Dataset

class ExtraTreesFeatureSelection:

    def __init__(self, training_dataset, target_column='LABEL'):

        #Column that contains the LABEL
        self.target_column = target_column

        if (not isinstance(training_dataset, pd.DataFrame)):
            raise Exception(f"The argument dataset must be a instance of Dataset class. Instead {type(training_dataset)} were provided.")
        
        if not len(training_dataset) > 0:
            raise Exception(f"The trainning dataset must to have at least one data point")

        # Removing undesired columns
        self.dataset = training_dataset.drop(['HOUR', 'MINUTE', 'SECOND', 'TRAIN', 'DATETIME', 'POSIXTIME'], axis=1, errors='ignore')

    def getImportancesDataFrame(self, n_estimators=100, random_state=1):
        np.random.seed(1)
        model = ExtraTreesClassifier(n_estimators=n_estimators, random_state=random_state)

        # Separating the dependent and independent variables
        # The use of x and y variables are a convention in ML codes
        y = self.dataset[self.target_column]
        x = self.dataset.drop(self.target_column, axis = 1)

        model.fit(x, y)

        feature_importance = model.feature_importances_

        # Normalizing the individual importances
        # feature_importance_normalized = np.std([tree.feature_importances_ for tree in
        #                                 model.estimators_],
        #                                 axis = 0)
        
        # Creating a DataFrame with the the Feature Selection result
        df = pd.DataFrame(feature_importance, index=x.columns, columns=['importance'])
        df.sort_values(by=['importance'], ascending=False, inplace=True)
        return df

    # Extremely Randomized Trees Classifier(Extra Trees Classifier)    
    # Important to pass just the TRAINING DATASET
    def getSelectedFeatures(self, topFeatures=10, n_estimators=100, random_state=1):
        df = self.getImportancesDataFrame(n_estimators=n_estimators, random_state=random_state)
        return list(df.iloc[:topFeatures].index)
        

