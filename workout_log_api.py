import requests
import json
from datetime import datetime
from flask import Flask, render_template, redirect, g, request, url_for, jsonify, Response, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/jake/Downloads/workout_log/workout_log.db'
db = SQLAlchemy(app)

# HELPERS
def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

# MODELS
class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    exercise = db.relationship('Exercise', backref='exercise', lazy='dynamic')

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    bodyweight = db.Column(db.Numeric)
    exercises = db.relationship('Exercise', backref='workout', lazy='dynamic')

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'date'       : dump_datetime(self.date),
           'notes'      : self.notes,
           'bodyweight' : self.bodyweight,          
           'exercises'  : self.exercises_serialized
       }
    @property
    def exercises_serialized(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ exercise.serialize for exercise in self.exercises]

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), primary_key=True)
    order = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'))
    sets = db.relationship('Set', backref='exercise', lazy='dynamic')

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'workout_id'    : self.workout_id,
           'order'      : self.order,
           'exercise_id' : self.exercise_id,          
           'sets'  : self.sets_serialized
       }    

    @property
    def sets_serialized(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ set.serialize for set in self.sets]       

class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Numeric)
    reps = db.Column(db.Integer)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), primary_key=True)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'order'      : self.order,
           'weight' : str(self.weight),                     
           'reps'  : self.reps,
           'exercise_id' : self.exercise_id
       }        

# ROUTES
@app.before_request
def before_request():
    url = 'https://wger.de/api/v2/exercise?status=2'
    headers = {'Accept': 'application/json', 'Authorization': 'Token 8fafb5c8ad07910ec31754c657649a8559c311a7'}
    r = requests.get(url=url, headers=headers)
    
    resp = r.content
    exercises = json.loads(resp)['results']
    exercise_names = [d['name'] for d in exercises]
    for exercise in exercise_names:
      exercise_record = Exercises(name=exercise)
      db.session.add(exercise_record)

@app.route("/app.js")
def app_js():
    return redirect(url_for('static', filename='app.js'))

@app.route("/")
def home():
    return render_template('index.html') 

@app.route("/workouts")
def workouts():
    result = Workout.query.all()
    print result
    workouts = [d.serialize for d in result]
    return jsonify(workouts)

@app.route("/exercises")
def exercises():
    result = Exercises.query.all()
    print result
    exercises = [{'id': d.id, 'name': d.name} for d in result]
    return jsonify(exercises)

@app.route('/add_workout', methods=['POST', 'GET'])
def add_workout():
    if request.method == 'POST':
        print request
        workout = Workout(date=datetime.utcnow())

        exercise_count = int(request.form['exercise_count'])

        for exercise_num in range(1,exercise_count + 1):
            exercise = Exercise(order=exercise_num, exercise_id=request.form['exercise'+str(exercise_num)], workout=workout)

            weights = request.form.getlist('weight' + str(exercise_num))
            reps = request.form.getlist('reps' + str(exercise_num))

            set_order = 1
            for weight, rep in zip(weights, reps):
                work_set = Set(order=set_order, exercise=exercise, weight=weight, reps=rep)
                set_order += 1

        db.session.add(workout)
        db.session.commit()

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

if __name__ == "__main__":
    app.run("0.0.0.0", port=5001)