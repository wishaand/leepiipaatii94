from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Wachtwoord", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Inloggen")

class RegisterForm(FlaskForm):
    voornaam = StringField("Voornaam", validators=[DataRequired(), Length(max=64)])
    achternaam = StringField("Achternaam", validators=[DataRequired(), Length(max=64)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Wachtwoord", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Herhaal wachtwoord", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Maak account")

class ContactForm(FlaskForm):
    naam = StringField("Naam", validators=[DataRequired(), Length(max=100)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    telefoon = StringField("Telefoon", validators=[Length(max=20)])
    onderwerp = StringField("Onderwerp", validators=[DataRequired(), Length(max=200)])
    bericht = TextAreaField("Bericht", validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField("Verstuur")