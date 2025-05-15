from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, DecimalField, SelectField, TextAreaField, FileField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileAllowed

def not_whitespace(form, field):
    if not field.data or field.data.strip() == '':
        raise ValidationError("This field cannot be blank.")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')

class ReviewForm(FlaskForm):
    restaurant = StringField('Restaurant Name', validators=[DataRequired(), not_whitespace])
    location = StringField('Location', validators=[DataRequired(), not_whitespace])
    cuisine = SelectField('Cuisine Type', choices=[
        ('', 'Choose...'), ('Japanese', 'Japanese'), ('Italian', 'Italian'),
        ('Chinese', 'Chinese'), ('Indian', 'Indian'), ('Mexican', 'Mexican'),
        ('Thai', 'Thai'), ('American', 'American'), ('Mediterranean', 'Mediterranean'),
        ('Korean', 'Korean'), ('Vietnamese', 'Vietnamese'), ('Other', 'Other')
    ], validators=[DataRequired(), not_whitespace])
    rating = SelectField('Your Rating', choices=[
        ('', 'Choose...'), ('1', '1 - Poor'), ('2', '2 - Fair'),
        ('3', '3 - Good'), ('4', '4 - Very Good'), ('5', '5 - Excellent')
    ], validators=[DataRequired(), not_whitespace])
    date = DateField('Date of Visit', format='%Y-%m-%d', validators=[DataRequired()])
    spend = DecimalField('Amount Spent ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    review_image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Rating')
