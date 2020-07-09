# jsp.py

# Imports
from flask import Flask, request, jsonify
import pandas as pd
import pickle
import json

app = Flask(__name__)  # class initiation
app.config['JSON_AS_ASCII'] = False

# Handlers
@app.route('/positions', methods=['GET'])
def get_positions():
    df = pd.read_csv('/data/data.csv')
    uniq_pos = set(df['positions'])
    pos_list = list(uniq_pos)
    return jsonify ({'Positions:': pos_list})


@app.route('/jsp', methods=['GET'])
def get_predict():
    data = request.data
    data_dict = json.loads(data)
    position = data_dict['position']
    gender = data_dict['gender']
    city = data_dict['city']
    age = data_dict['age']
    experience = data_dict['experience']

    with open('jsp_model.pkl', 'rb') as pkl_file:
        regressor = pickle.load(pkl_file)

    predict = regressor.predict([position, gender, city, age, experience])
    return jsonify({'JobSalaryPrediction, RUR': int(round(predict * 1000, 0))})


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
