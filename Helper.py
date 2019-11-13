import pandas as pd
import numpy as np
import math, re, os, shutil, time
from enum import Enum
from IPython.display import Markdown, display, HTML
import matplotlib.pyplot as plt

class Utils:

    def __init__(self):
        metrics = ['Model', 'Feature Description', 'RMSE', 'R2 Score', 'Selected Features']
        self.evalmetrics = pd.DataFrame(columns= metrics)
     
    def printHtml(self, string, bold = True):
        if ( bold == True):
            display(HTML('<b>' + string + '</b>'))
        else:
            display(HTML(string))

    def display_data(self, title, data, count):
        self.printHtml(title)
        with pd.option_context('display.max_rows', count, 'display.max_columns', None):
            display(data)

    def display_data_all(self, title, data):
        self.printHtml(title)
        display(data)
            
    def extract_numeric(self, v):
        return pd.to_numeric(re.sub(r'[^0-9.]+', '', v))

  
    # Function to evaluate model metrics
    def evaluate_model(self, category, modelType, RMSE, Score, true_target, predicted_target, coeffs, columns):
        modelTitle = '{0} - RMSE:{1}, R2 Score:{2}'.format(modelType, round(RMSE,2), round(Score,2))
        important_features = pd.Series(data=coeffs,index=columns)
        important_features.sort_values(ascending=False,inplace=True)
        imp_features_display = important_features[:5].apply(lambda x:round(x,2)).to_csv(header=None, index=True).strip('\n').split('\n')

        self.evalmetrics = self.evalmetrics.append({'Model':  modelType, 
                                        'Feature Description':category,
                                        'RMSE': RMSE, 
                                        'R2 Score':Score,
                                        'Selected Features': imp_features_display
                                    }, ignore_index=True)

        f, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12,4));    
        ax1.scatter(true_target, predicted_target, label='Actual vs Predicted');
        ax1.set(xlabel='Actual', ylabel='Predicted', title= modelTitle)
        ax2.set(title=modelType + ' - Feature Importance')
        important_features.plot(kind='bar', ax=ax2);
        
    def print_metrics(self, title):
        self.printHtml(title)
        pd.set_option('display.max_colwidth', -1)    
        display(self.evalmetrics.sort_values(by='R2 Score', ascending=False))

    

  
  
