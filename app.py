from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now())
    bmis = db.relationship('BMI', backref='user', lazy=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email')

# Body Mass Index class/model


class BMI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    bmi_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, weight, height, bmi, status, user):
        self.weight = weight
        self.height = height
        self.bmi = bmi
        self.status = status
        self.user = user

# BMI schema


class BMISchema(ma.Schema):
    class Meta:
        fields = ('id', 'weight', 'height', 'bmi',
                  'status', 'bmi_date')

# init schema


bmi_schema = BMISchema()
bmis_schema = BMISchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/bmi/register', methods=['POST'])
def register_user():

    print(request.json)
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    user = getUser(email)

    if user:
        return jsonify({"msg": "Email is already in use"}), 400

    hash_password = generate_password_hash(password)
    new_user = User(name, email, hash_password)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201


@app.route('/bmi', methods=['POST'])
@jwt_required
def add_bmi():
    weight = request.json['weight']
    height = request.json['height']
    bmi = request.json['bmi']
    status = request.json['status']

    if not weight:
        return jsonify({"msg": "Weight status is required"}), 400
    if not height:
        return jsonify({"msg": "Height status is required"}), 400
    if not status:
        return jsonify({"msg": "BMI status is required"}), 400
    if not bmi:
        return jsonify({"msg": "BMI value is required"}), 400

    current_user_email = get_jwt_identity()
    user = getUser(current_user_email)
    print(f"user:  ", user)

    user_dump = user_schema.dump(user)
    print(f"user_dump: ", user_dump)

    new_bmi = BMI(weight, height, bmi, status, user)

    db.session.add(new_bmi)
    db.session.commit()

    return bmi_schema.jsonify(new_bmi), 201


@app.route('/bmi', methods=['GET'])
@jwt_required
def get_bmis():
    all_bmi = BMI.query.all()

    result = bmis_schema.dump(all_bmi)

    print(f"Results is {result}")
    return jsonify(result)


@app.route('/bmi/<id>', methods=['GET'])
@jwt_required
def get_bmi(id):
    bmi = BMI.query.get(id)
    print(f"BMI is {bmi}")
    return bmis_schema.jsonify(bmi)


@app.route('/user/bmi', methods=['GET'])
@jwt_required
def get_user_bmi():
    current_user_email = get_jwt_identity()
    user = getUser(current_user_email)

    bmis = BMI.query.filter(BMI.user_id == user.id).all()
    print(f"BMI is {bmis}")
    return bmis_schema.jsonify(bmis)


# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'change-this-for-prod'  # Change this!
jwt = JWTManager(app)


@app.route('/bmi/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = getUser(email)

    if not user:
        return jsonify({"msg": "Username does not exist"}), 401
    if not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200


def getUser(email):
    return User.query.filter_by(email=email).first()
