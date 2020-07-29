# jsp.py
# Модуль для "обвязки" модели машинного обучения декоратором Flask

# Imports
from flask import Flask, request, jsonify, render_template
import pandas as pd
import pickle
import json

app = Flask(__name__)  # class initiation
app.config['JSON_AS_ASCII'] = False

# Deserialization and load model
with open('jsp_model.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

# Handlers
@app.route('/predict', methods=['POST'])
def predict():
    """For rendering results on HTML GUI"""
    data_dict = request.form
    position = data_dict['position']
    gender = data_dict['gender']
    city = data_dict['city']
    age = data_dict['age']
    age = int(age)
    experience = data_dict['experience']
    experience = int(experience)
    output = regressor.predict([position, gender, city, age, experience])
    return render_template('index.html', prediction_text=f'JobSalaryPrediction, RUR: {int(output * 1000)}')


@app.route('/positions', methods=['GET'])
def get_positions():
    """Return unique positions list"""
    df = pd.read_csv('/data/data.csv')
    uniq_pos = set(df['positions'])
    pos_list = list(uniq_pos)
    return jsonify ({'Positions:': pos_list})


@app.route('/jsp', methods=['GET'])
def get_predict():
    """For predicting through API"""
    data = request.data
    data_dict = json.loads(data)
    position = data_dict['position']
    gender = data_dict['gender']
    city = data_dict['city']
    age = data_dict['age']
    experience = data_dict['experience']
    predict = regressor.predict([position, gender, city, age, experience])
    return jsonify({'JobSalaryPrediction, RUR': int(round(predict * 1000, 0))})


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
