from flask_wtf import FlaskForm          # Basisformulier met CSRF-bescherming
from wtforms import (
    StringField,                         # Tekstveld (1 regel)
    PasswordField,                       # Wachtwoordveld (verborgen tekst)
    SubmitField,                         # Verstuurknop
    TextAreaField,                       # Groot tekstvak (meerdere regels)
    BooleanField                         # Checkbox (true/false)
)
from wtforms.validators import (
    DataRequired,                        # Veld moet ingevuld zijn
    Email,                               # Moet een geldig e-mailadres zijn
    EqualTo,                             # Moet gelijk zijn aan ander veld
    Length                               # Minimale/maximale lengte
)


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Wachtwoord", validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField("Onthoud mij")
    submit = SubmitField("Inloggen")


class RegisterForm(FlaskForm):
    voornaam = StringField("Voornaam", validators=[DataRequired(), Length(max=64)])
    achternaam = StringField("Achternaam", validators=[DataRequired(), Length(max=64)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Wachtwoord", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Herhaal wachtwoord", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Maak account")


class ContactForm(FlaskForm):
    naam = StringField("Naam", validators=[DataRequired(), Length(max=100)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    telefoon = StringField("Telefoon", validators=[Length(max=20)])  
    onderwerp = StringField("Onderwerp", validators=[DataRequired(), Length(max=200)])
    bericht = TextAreaField("Bericht", validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField("Verstuur")


class ChangePasswordForm(FlaskForm):
    """Formulier voor wachtwoord wijzigen"""
    current_password = PasswordField("Huidig wachtwoord", validators=[DataRequired()])
    new_password = PasswordField("Nieuw wachtwoord", validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField("Bevestig nieuw wachtwoord", validators=[DataRequired(), EqualTo("new_password", message="Wachtwoorden komen niet overeen")])
    submit = SubmitField("Wachtwoord wijzigen")


class PasswordResetRequestForm(FlaskForm):
    """Formulier om wachtwoord reset aan te vragen"""
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField("Verstuur reset link")


class PasswordResetForm(FlaskForm):
    """Formulier om nieuw wachtwoord in te stellen"""
    password = PasswordField("Nieuw wachtwoord", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Bevestig nieuw wachtwoord", validators=[DataRequired(), EqualTo("password", message="Wachtwoorden komen niet overeen")])
    submit = SubmitField("Reset wachtwoord")