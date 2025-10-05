import schedule
import time
from db import Attendee
from email_agent import send_email
from flask import Flask

def send_pre_event_reminders(app):
    with app.app_context():
        attendees = Attendee.query.filter_by(engaged=False).all()
        for user in attendees:
            send_email(user.email, "Reminder: Upcoming Webinar",
                       f"Hi {user.name},\nDon't miss our webinar on {user.interest}!")

def send_post_event_followups(app):
    with app.app_context():
        attendees = Attendee.query.all()
        for user in attendees:
            send_email(user.email, "Thank You for Attending",
                       f"Hi {user.name},\nThank you for joining the webinar on {user.interest}. Here's a feedback survey link!")

def run_scheduler(app):
    schedule.every().day.at("09:00").do(send_pre_event_reminders, app)
    schedule.every().day.at("18:00").do(send_post_event_followups, app)

    while True:
        schedule.run_pending()
        time.sleep(60)
