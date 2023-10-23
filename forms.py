from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, SelectField, DateField, \
    BooleanField, FileField, TimeField, RadioField, TextAreaField
from wtforms.validators import DataRequired, URL, Email, InputRequired
from flask_ckeditor import CKEditorField


class IceBreaker(FlaskForm):
    """admin form to adds ice breaker questions """
    question_number = StringField("Question Number", validators=[DataRequired()], default=1)
    question = TextAreaField("Question ", validators=[DataRequired()])
    Save = SubmitField("Save")


class QuizQuestion(FlaskForm):
    """admin form to add quizz questions"""
    question_number = StringField("Question Number", validators=[DataRequired()], default=1)
    question = CKEditorField("Question ", validators=[DataRequired()])
    option_1 = StringField("Option A", validators=[InputRequired()])
    option_2 = StringField("Option B", validators=[InputRequired()])
    option_3 = StringField("Option C", validators=[InputRequired()])
    option_4 = StringField("Option D", validators=[InputRequired()])
    answer = StringField("Answer ", validators=[DataRequired()])
    Save = SubmitField("Save")


class PickIcebreaker(FlaskForm):
    pick = SubmitField("Pick Question")


class Registration(FlaskForm):
    """asks user for their information"""
    full_name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()],
                               render_kw={"placeholder": "Whatsapp Number"})
    save = SubmitField("Save")


class QuizReg(FlaskForm):
    phone_number = StringField("Phone Number", validators=[DataRequired()], render_kw={"placeholder": "Enter the "
                                                                                                      "number you "
                                                                                                      "registered "
                                                                                                      "with"})
    submit = SubmitField("Show Quiz")


class Export(FlaskForm):
    export = SubmitField("Export")


class DeleteAllQuestion(FlaskForm):
    delete = SubmitField("Delete all Question")


class RetryQuiz(FlaskForm):
    submit = SubmitField("Retry")


class HomeQuiz(FlaskForm):
    submit = SubmitField("Home")


class FacilitatorsRating(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    facilitators_name = StringField("Name of Facilitator", validators=[DataRequired()])
    module = StringField("Name of Module", validators=[DataRequired()])

    q1 = RadioField("1. The presentation met my expectations.", choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                                                                         ('3', 'Neutral'), ('2', 'Disagree'),
                                                                         ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])

    q2 = RadioField("2. The training objectives for the module were identified and followed.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'), ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])

    q3 = RadioField("3. Main points/principles were made Clear.", choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                                                                           ('3', 'Neutral'), ('2', 'Disagree'),
                                                                           ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])

    q4 = RadioField("4. The content was organized and easy to follow.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'), ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])
    q5 = RadioField("5. The trainer use of voice, examples, gestures were adequate.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'), ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])
    q6 = RadioField("6. The quality of instruction was good and easy to apply.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'), ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])

    q7 = RadioField("7. The trainer used appropriate introduction and conclusion.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'), ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])

    q8 = RadioField("8. Class participation and interaction were encouraged.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'),
                             ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])
    q9 = RadioField("9. Handling of questions and discussion was adequate.",
                    choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                             ('3', 'Neutral'), ('2', 'Disagree'),
                             ('1', 'Strongly Disagree')],
                    validators=[DataRequired()])

    q10 = RadioField("10. Timing of the session was adequate.", choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                                                                         ('3', 'Neutral'), ('2', 'Disagree'),
                                                                         ('1', 'Strongly Disagree')],
                     validators=[DataRequired()])
    q11 = RadioField("11. Use of different learning methods were adequate.",
                     choices=[('5', 'Strongly Agree'), ('4', 'Agree'),
                              ('3', 'Neutral'), ('2', 'Disagree'),
                              ('1', 'Strongly Disagree')],
                     validators=[DataRequired()])
    q12 = RadioField("12. Give your overall rating of this facilitator:",
                     choices=[('5', 'Excellent'), ('4', 'Very Good'),
                              ('3', 'Good'), ('2', 'Average'),
                              ('1', 'poor')],
                     validators=[DataRequired()])
    comment = TextAreaField("Other comments", validators=[DataRequired()])

    submit = SubmitField("Submit Rating")
