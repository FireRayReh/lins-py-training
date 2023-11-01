import csv
import random
import tempfile
import os

from flask import Flask, abort, render_template, redirect, url_for, flash, request, session, Response, jsonify
from flask_bootstrap import Bootstrap5
# from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
from forms import IceBreaker, QuizQuestion, PickIcebreaker, Registration, DeleteAllQuestion, Export, QuizReg, HomeQuiz, \
    FacilitatorsRating, Formsreg, AddSuccess, DeletePicked

import pandas as pd

#

app = Flask(__name__)
Bootstrap5(app)

app.config['SECRET_KEY'] = 'secretkey'
ckeditor = CKEditor(app)

"""db connecting"""
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('db_credentials')

db = SQLAlchemy()
db.init_app(app)


# Configure Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)
#
#
# @login_manager.user_loader
# def load_user(user_id):
#     return db.get_or_404(Users, user_id)


class Icebreakerdb(db.Model):
    """holds the icebreaker questions, questions are removed every time any user picks the question"""

    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.String(250))
    question = db.Column(db.String(250))


class QuizDb(db.Model):
    __tablename__ = "question"
    """holds the individual question data as well as their options"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(250))
    options = db.relationship('Option', backref='question', lazy=True)
    answer = db.Column(db.String(250))


class Option(db.Model):
    __tablename__ = "option"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(255), nullable=False)


class PickedUsersDb(db.Model):
    __tablename__ = "pickedusers"
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(255), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/admin", methods=["POST", "GET"])
def admin():
    """admin operator home page"""
    users = db.session.execute(db.Select(Users)).scalars().all()
    number_of_users = len(users)
    export = Export()
    delete = DeleteAllQuestion()
    name = []
    email = []
    phone_number = []
    if export.validate_on_submit():
        for user in users:
            name.append(user.full_name)
            email.append(user.email)
            phone_number.append(user.phone_number)
        data = {
            "Name": name,
            "Email": email,
            "Phone Number": phone_number,
        }

        df = pd.DataFrame(data)
        csv_data = df.to_csv(index=False)

        # Send the CSV file as a downloadable attachment
        response = Response(csv_data, content_type='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        return response

    if delete.validate_on_submit():
        db.session.query(Users).delete()
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("admin.html", users=users, number_of_users=number_of_users, export=export, delete=delete)


@app.route("/admin/add-question", methods=["POST", "GET"])
def add_question():
    """admin operator, adds question to the quiz question database"""
    form = QuizQuestion()
    if form.validate_on_submit():
        question_num = form.question_number.data
        question = form.question.data
        option_1 = form.option_1.data
        option_2 = form.option_2.data
        option_3 = form.option_3.data
        option_4 = form.option_4.data
        answer = form.answer.data
        options = [option_1, option_2, option_3, option_4]

        existing_question = db.session.execute(
            db.Select(QuizDb).where(QuizDb.id == int(question_num))).scalar()

        if not existing_question:
            new_question = QuizDb(question=question,
                                  answer=answer)
            for option in options:
                new_options = Option(text=option, question=new_question)
                db.session.add(new_options)
                db.session.commit()

        else:
            existing_question.question = question
            existing_question.answer = answer

            options = [option_1, option_2, option_3, option_4]

            index = 0
            for option in existing_question.options:
                if index <= len(existing_question.options):
                    option.text = options[index]
                    index += 1
                    db.session.commit()

            db.session.commit()
            # for option in options:
            #     new_options = Option(text=option, question=existing_question)
            #     db.session.add(new_options)
            #     db.session.commit()

        return redirect(url_for("question_success"))

    return render_template("add-question.html", form=form)


@app.route("/question_success", methods=["POST", "GET"])
def question_success():
    form = AddSuccess()
    if form.validate_on_submit():
        return redirect(url_for("add_question"))

    return render_template("icebreaker-success.html", form=form)


@app.route("/admin/icebreaker", methods=["GET", "POST"])
def add_icebreaker():
    """admin operator, can add question to the icebreaker database"""
    form = IceBreaker()
    if form.validate_on_submit():

        question = form.question.data
        question_number = form.question_number.data
        existing_question = db.session.execute(
            db.Select(Icebreakerdb).where(Icebreakerdb.question_number == question_number)).scalar()
        if not existing_question:
            new_question = Icebreakerdb(
                question_number=question_number,
                question=question
            )
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for("icebreaker_success"))

        else:
            existing_question.question = question
            db.session.commit()

            return redirect(url_for("icebreaker_success"))

    return render_template("add-icebreaker.html", form=form)


@app.route("/icebreaker_success", methods=["POST", "GET"])
def icebreaker_success():
    form = AddSuccess()
    if form.validate_on_submit():
        return redirect(url_for("add_icebreaker"))

    return render_template("icebreaker-success.html", form=form)


@app.route("/view-quiz-question", methods=["GET", "POST"])
def view_quiz_question():
    """displays all the quiz questions for admin to see, displays delete and delete all buttons"""
    form = DeleteAllQuestion()
    if form.validate_on_submit():
        return redirect(url_for("delete_all_questions"))
    quiz_question = db.session.execute(db.select(QuizDb)).scalars().all()
    return render_template("view-quiz-question.html", quiz_question=quiz_question, form=form)


@app.route("/view-ice-breaker", methods=["GET", "POST"])
def view_ice_breaker():
    """displays all icebreaker questions for admin and also delete and delete all button """
    form = DeleteAllQuestion()
    if form.validate_on_submit():
        return redirect(url_for("delete_all_icebreaker"))

    ice_breaker = db.session.execute(db.select(Icebreakerdb)).scalars().all()
    return render_template("view-ice-breaker.html", ice_breaker=ice_breaker, form=form)


@app.route("/delete/all-question")
def delete_all_questions():
    """deletes all the quiz questions from the database"""
    db.session.query(QuizDb).delete()
    db.session.query(Option).delete()
    db.session.commit()
    return redirect(url_for("view_quiz_question"))

@app.route("/delete/all-icebreaker")
def delete_all_icebreaker():
    """deletes all the icebreaker questions from the database"""
    db.session.query(Icebreakerdb).delete()
    db.session.commit()
    return redirect(url_for("view_ice_breaker"))



@app.route("/delete/<int:question_id>")
def delete_question(question_id):
    """deletes single question from the db"""
    question = db.session.execute(db.Select(QuizDb).where(QuizDb.id == question_id)).scalar()

    db.session.delete(question)
    db.session.commit()

    return redirect(url_for("view_quiz_question"))
    # return f"{question_id}"


@app.route("/delete-icebreaker/<int:question_id>")
def delete_icebreaker(question_id):
    """deletes single icebreaker from the db"""
    question = db.session.execute(db.Select(Icebreakerdb).where(Icebreakerdb.id == question_id)).scalar()
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("view_ice_breaker"))


@app.route("/delete-all-users")
def delete_all_users():
    """deletes all the users from the database"""
    db.session.query(Users).delete()
    db.session.commit()

    return redirect(url_for("admin"))


@app.route("/others", methods=["GET", "POST"])
def others():
    form = DeletePicked()
    users = db.session.execute(db.Select(PickedUsersDb)).scalars().all()

    if form.validate_on_submit():
        db.session.query(PickedUsersDb).delete()
        db.session.commit()
        return redirect(url_for("others"))

    return render_template("admin-other.html", form=form, users=users, count=len(users))


@app.route("/", methods=["GET", "POST"])
def home():
    """Home page"""
    form = Registration()
    if form.validate_on_submit():
        existing_user = db.session.execute(
            db.Select(Users).where(Users.phone_number == form.phone_number.data)).scalar()

        if existing_user:
            flash(message=f"You have already Registered {existing_user.full_name}", category="message")
            # return redirect(url_for("home"))

        else:
            new_user = Users(
                full_name=form.full_name.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
            )
            db.session.add(new_user)
            db.session.commit()

            flash(message=f"You have successfully registered", category="message")
            return redirect(url_for("home"))

    return render_template("index.html", form=form)


@app.route("/icebreaker", methods=["GET", "POST"])
def icebreaker():
    """displays a pick question button and asks the user to pick question"""
    form = PickIcebreaker()
    if form.validate_on_submit():

        user = db.session.execute(db.Select(Users).where(Users.phone_number == form.number.data)).scalar()
        if user:
            picked = db.session.execute(
                db.Select(PickedUsersDb).where(PickedUsersDb.phone_number == form.number.data)).scalar()
            if picked:
                flash("You have already picked a question")
                return redirect(url_for("icebreaker"))
            else:
                return redirect(url_for("icebreaker_question", user=form.number.data))
        else:
            flash("Please make sure you have registered")
            return redirect(url_for("icebreaker"))

    return render_template("ice-breaker.html", form=form)


@app.route("/icebreaker/question/<user>", methods=["GET", "POST"])
def icebreaker_question(user):
    """displays a random icebreaker question and then deletes the question from the question database"""
    picked = db.session.execute(db.Select(PickedUsersDb).where(PickedUsersDb.phone_number == user)).scalar()
    if picked:
        return "<h1>You have already picked a question</h1>"
    try:
        questions = db.session.execute(db.Select(Icebreakerdb)).scalars().all()
        random_question = random.choice(questions)
        db.session.delete(random_question)
        db.session.commit()

        new_picked = PickedUsersDb(
            phone_number=user,
        )
        db.session.add(new_picked)
        db.session.commit()

        return render_template("icebreaker-question.html", question=random_question)
    except IndexError:
        # Handle the IndexError gracefully
        return "<h1>Sorry no Questions yet</h1>"


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    """prompts the user to enter their phone number """
    form = QuizReg()
    if form.validate_on_submit():
        user = db.session.execute(db.Select(Users).where(Users.phone_number == form.phone_number.data)).scalar()
        if user:
            session["name"] = user.full_name
            return redirect(url_for("show_quiz"))

        else:
            flash("Please make sure you have registered")
            return redirect(url_for("quiz"))

    return render_template("quiz.html", form=form)


questions = [
    {
        'question': 'What is the capital of France?',
        'choices': ['Paris', 'London', 'Berlin', 'Madrid'],
        'correct_answer': 'Paris',
    },
    {
        'question': 'Which planet is known as the Red Planet?',
        'choices': ['Mars', 'Venus', 'Jupiter', 'Mercury'],
        'correct_answer': 'Mars',
    },
]

question_no = 0
score = 0


@app.route("/quiz/question", methods=["GET", "POST"])
def show_quiz():
    """shows the individual quiz question and their option, checks the user answer against the correct answer and
    global question_no, score
    name = session.get("name")
    question_list = QuizDb.query.all()
    
    if request.method == "POST":
        user_answer = request.form.get("choice")
        if question_no < len(question_list):
            correct_answer = question_list[question_no].answer
            question_no += 1
            if user_answer == correct_answer:
                score += 1
            if question_no < len(question_list):
                return redirect(url_for("show_quiz"))
            else:
                return redirect(url_for("quiz_result"))

    if question_no < len(question_list):
        current_question = question_list[question_no]
        return render_template("quiz-question.html", question=current_question, name=name, index=(question_no + 1), total=len(question_list))
    else:
        question_no = 0
        score = 0
        if question_list:
            current_question = question_list[question_no]
            return render_template("quiz-question.html", question=current_question, name=name, index=(question_no + 1), total=len(question_list))
        else:
            # Handle the case when question_list is empty
            return redirect(url_for("quiz_result"))


@app.route("/quiz-result", methods=['GET', 'POST'])
def quiz_result():
    """displays the quiz result"""
    global score
    question_list = QuizDb.query.all()
    name = session.get("name")

    return render_template("quiz-result.html", name=name, score=score, total=len(question_list))


@app.route("/forms/facilitators", methods=["GET", "POST"])
def forms_facilitator():
    """asks user to enter their phone number, checks if they are registered before allowing them to fill survey"""
    form = Formsreg()
    if form.validate_on_submit():
        number = form.phone_number.data
        user = db.session.execute(db.Select(Users).where(Users.phone_number == number)).scalar()

        if user:
            return redirect(url_for("facilitators_rating"))
        else:
            flash("Please make sure you have registered")
            return redirect(url_for("forms_facilitator"))

    return render_template("forms-facilitator.html", form=form)


@app.route("/forms/course-evaluation", methods=["GET", "POST"])
def forms_course_evaluation():
    """asks user to enter their phone number, checks if they are registered before allowing them to fill survey"""
    form = Formsreg()
    if form.validate_on_submit():
        number = form.phone_number.data
        user = db.session.execute(db.Select(Users).where(Users.phone_number == number)).scalar()

        if user:
            return redirect(url_for("course_evaluation"))
        else:
            flash("Please make sure you have registered")
            return redirect(url_for("forms_course_evaluation"))

    return render_template("forms-course-evaluation.html", form=form)


@app.route("/facilitators-rating")
def facilitators_rating():
    """displays a Google form for the survey"""
    form = FacilitatorsRating()
    return render_template("facilitators-rating.html", form=form)


@app.route("/course-evaluation")
def course_evaluation():
    """displays a Google form for the survey"""
    return render_template("course-evaluation.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5004)
