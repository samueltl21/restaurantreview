from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, DecimalField, SelectField, TextAreaField, Optional
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

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
    restaurant = StringField('Restaurant Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    cuisine = SelectField('Cuisine Type', choices=[
        ('', 'Choose...'),
        ('Japanese', 'Japanese'), ('Italian', 'Italian'), ('Chinese', 'Chinese'),
        ('Indian', 'Indian'), ('Mexican', 'Mexican'), ('Thai', 'Thai'),
        ('American', 'American'), ('Mediterranean', 'Mediterranean'),
        ('Korean', 'Korean'), ('Vietnamese', 'Vietnamese'), ('Other', 'Other')
    ], validators=[DataRequired()])
    date = DateField('Date of Visit', format='%Y-%m-%d', validators=[DataRequired()])
    rating = SelectField('Your Rating', choices=[
        ('', 'Choose...'),
        ('1', '1 - Poor'), ('2', '2 - Fair'), ('3', '3 - Good'),
        ('4', '4 - Very Good'), ('5', '5 - Excellent')
    ], validators=[DataRequired()])
    spend = DecimalField('Amount Spent ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    review_image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Rating')
