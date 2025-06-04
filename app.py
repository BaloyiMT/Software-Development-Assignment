from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DB_NAME = 'database.db'


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                dob TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                food TEXT NOT NULL,
                watch_movies INTEGER NOT NULL,
                listen_radio INTEGER NOT NULL,
                eat_out INTEGER NOT NULL,
                watch_tv INTEGER NOT NULL
            );
        ''')
        conn.commit()


init_db()


@app.route('/')
def survey():
    return render_template('survey.html')


@app.route('/submit', methods=['POST'])
def submit():
    try:

        dob = request.form.get("dob")
        age = calculate_age(dob)
        if age < 5 or age > 120:
            flash("Age must be between 5 and 120 years.")
            return redirect(url_for('survey'))

        name = request.form.get("name")
        email = request.form.get("email")
        dob = request.form.get("dob")
        contact_number = request.form.get("contact-number")
        food = ', '.join(request.form.getlist("food"))
        watch_movies = int(request.form.get("movies"))
        listen_radio = int(request.form.get("radio"))
        eat_out = int(request.form.get("eatout"))
        watch_tv = int(request.form.get("watchtv"))

        if not all([name, email, dob, contact_number, food]):
            flash("All fields must be filled.")
            return redirect(url_for('survey'))

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                INSERT INTO surveys (
                    name, email, dob, contact_number, food,
                    watch_movies, listen_radio, eat_out, watch_tv
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, dob, contact_number, food, watch_movies, listen_radio, eat_out, watch_tv))
            conn.commit()
            flash("Survey submitted successfully!")
    except Exception as e:
        flash("Error: " + str(e))

    return redirect(url_for('survey'))


@app.route('/results')
def results():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM surveys")
        rows = cursor.fetchall()

        if not rows:
            return render_template("results.html", data=None)

        total = len(rows)
        ages = [calculate_age(row[3]) for row in rows]

        food_counts = {'Pizza': 0, 'Pasta': 0, 'Pap and Wors': 0}
        for row in rows:
            for food in food_counts:
                if food in row[5]:
                    food_counts[food] += 1

        data = {
            'total': total,
            'avg_age': round(sum(ages)/total, 1),
            'oldest': max(ages),
            'youngest': min(ages),
            'pizza_pct': round(food_counts['Pizza']/total*100, 1),
            'pasta_pct': round(food_counts['Pasta']/total*100, 1),
            'pap_pct': round(food_counts['Pap and Wors']/total*100, 1),
            'avg_watch_movies': round(sum([row[6] for row in rows])/total, 1),
            'avg_radio': round(sum([row[7] for row in rows])/total, 1),
            'avg_eat_out': round(sum([row[8] for row in rows])/total, 1),
            'avg_watch_tv': round(sum([row[9] for row in rows])/total, 1)
        }

        return render_template("results.html", data=data)


def calculate_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return -1


if __name__ == '__main__':
    app.run(debug=True)
