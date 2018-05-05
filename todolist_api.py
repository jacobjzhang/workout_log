# RESTful API
from flask import Flask, render_template, redirect, g, request, url_for, jsonify, Response
from workout_log_db import Workout, Exercises, Exercise, Set
# import sqlite3
import urllib
import json

DATABASE = 'todolist.db'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/add_workout', methods=['POST', 'GET'])
def add_workout():
    if request.method == 'POST':
        # user = User.query.filter_by(name=session['username']).first()

        workout = Workout(date=datetime.utcnow(), user_id=1)

        exercise_count = int(request.form['exercise_count'])

        for exercise_num in range(1,exercise_count + 1):
            exercise = Exercise(order=exercise_num, exercise_id=request.form['exercise'+str(exercise_num)], workout=workout)

            weights = request.form.getlist('weight' + str(exercise_num))
            reps = request.form.getlist('reps' + str(exercise_num))

            set_order = 1
            for weight, rep in zip(weights, reps):
                work_set = Set(order=set_order, exercise=exercise, weight=weight, reps=rep)
                set_order += 1

        db.add(workout)
        db.commit()

        return redirect(url_for('index'))

    exercises = Exercises.query.all()
    return render_template('add_workout.html', exercises=exercises)

@app.route("/api/items")  # default method is GET
def get_items():
    db = get_db()
    cur = db.execute('SELECT what_to_do, due_date, status FROM entries')
    entries = cur.fetchall()
    tdlist = [dict(what_to_do=row[0], due_date=row[1], status=row[2])
              for row in entries]
    response = Response(json.dumps(tdlist),  mimetype='application/json')
    return response


@app.route("/api/items", methods=['POST'])
def add_item():
    db = get_db()
    db.execute('insert into entries (what_to_do, due_date) values (?, ?)',
               [request.json['what_to_do'], request.json['due_date']])
    db.commit()
    return jsonify({"result": True})


@app.route("/api/items/<item>", methods=['DELETE'])
def delete_item(item):
    item = urllib.parse.unquote(item)
    db = get_db()
    db.execute("DELETE FROM entries WHERE what_to_do='"+item+"'")
    db.commit()
    return jsonify({"result": True})


@app.route("/api/items/<item>", methods=['PUT'])
def update_item(item):
    # we do not need the body so just ignore it
    item = urllib.parse.unquote(item)
    db = get_db()
    db.execute("UPDATE entries SET status='done' WHERE what_to_do='"+item+"'")
    db.commit()
    return jsonify({"result": True})


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001)