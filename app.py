from flask import Flask, render_template, request
from db import db, init_db, Attendee
import pandas as pd
from email_agent import send_email
import os


app = Flask(__name__)

# MySQL database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/event_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "uploads"

init_db(app)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Read CSV using pandas
            df = pd.read_csv(filepath)

            # Expected columns: name, email, interest
            for _, row in df.iterrows():
                if not Attendee.query.filter_by(email=row['email']).first():
                    new_user = Attendee(
                        name=row['name'],
                        email=row['email'],
                        interest=row['interest']
                    )
                    db.session.add(new_user)
                    db.session.commit()

                    # Send notification mail
                    send_email(
                        row['email'],
                        "Webinar Registration Confirmed",
                        f"Hi {row['name']},\nYou are registered for the webinar on {row['interest']}."
                    )

            return "<h2>File uploaded and notifications sent successfully!</h2>"

    return render_template('registration.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

