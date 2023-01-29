# run in jupyter
import pandas as pd

from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import shap
shap.initjs()

# # 1.example
X,y = shap.datasets.adult()
X, _, y, _ = train_test_split(X, y, test_size=0.9, random_state=7)
model = RandomForestClassifier().fit(X,y)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

X,y = shap.datasets.adult()
X, _, y, _ = train_test_split(X, y, test_size=0.9, random_state=7)
model = RandomForestClassifier().fit(X,y)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

shap.force_plot(explainer.expected_value[1], shap_values[1][:1000,:])

shap.summary_plot(shap_values[0], X)

shap.summary_plot(shap_values, X)


# # 2.shap value on trained model

folder_name = '2022'
data_path, model_path, score_path = f'data/training_data/{folder_name}', f'models/{folder_name}',  f'score/{folder_name}'
rf = load(f'{model_path}/rf_v0')
X_train = pd.read_csv(f'{data_path}/X_train.csv', encoding='utf-8')

pred, pred_proba = rf.predict(X_train), rf.predict_proba(X_train)
print(pred[0][0], pred_proba[0][0])

explainer = shap.TreeExplainer(rf, model_ouput='predict_proba') # model_ouput='predict_proba'
shap_values = explainer.shap_values(X_train)

expected_value = explainer.expected_value * 9
expected_value

shap_values = [i * 9 for i in shap_values]
shap.force_plot(expected_value[1], shap_values[1][0,:])
shap.force_plot(expected_value[0], shap_values[0][0,:])

shap_values = [v for i, v in enumerate(shap_values) if i % 2 == 1]
print(len(shap_values))

shap.summary_plot(shap_values, X_train)
shap.summary_plot(shap_values, X_train, max_display=50)

explainer.expected_value
shap_values[0][0]
shap.dependence_plot("years_in_company", shap_values[1], X_train)
shap.summary_plot(shap_values[0], X_train)
