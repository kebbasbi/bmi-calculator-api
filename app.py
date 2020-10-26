from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

# init app
app = Flask(__name__)
baseDir = os.path.abspath(os.path.dirname(__file__))
#print(f'baseDir {baseDir}')

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(baseDir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)

# init ma
ma = Marshmallow(app)

# Body Mass Index class/model


class BMI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    bmi_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.now())

    def __init__(self, weight, height, bmi, status, name):
        self.weight = weight
        self.height = height
        self.bmi = bmi
        self.status = status
        self.name = name

# BMI schema


class BMISchema(ma.Schema):
    class Meta:
        fields = ('id', 'weight', 'height', 'bmi',
                  'status', 'name', 'bmi_date')


# init schema

bmi_schema = BMISchema()
bmis_schema = BMISchema(many=True)


@app.route('/bmi', methods=['POST'])
def add_bmi():
    weight = request.json['weight']
    height = request.json['height']
    bmi = request.json['bmi']
    status = request.json['status']
    name = request.json['name']

    new_bmi = BMI(weight, height, bmi, status, name)

    db.session.add(new_bmi)
    db.session.commit()

    return bmi_schema.jsonify(new_bmi)


@app.route('/bmi', methods=['GET'])
def get_bmis():
    all_bmi = BMI.query.all()

    result = bmis_schema.dump(all_bmi)

    print(f"Results is {result}")
    return jsonify(result)


@app.route('/bmi/<id>', methods=['GET'])
def get_bmi(id):
    bmi = BMI.query.get(id)
    print(f"BMI is {bmi}")
    return bmi_schema.jsonify(bmi)


# run server
if __name__ == '__main__':
    app.run(debug=True)
