from app import db


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
