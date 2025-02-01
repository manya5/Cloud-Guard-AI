from flask_wtf import FlaskForm
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired, Email, ValidationError
from models import User  # Adjust this import based on your User model location

class EditProfileForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    email = EmailField('Email',
        validators=[DataRequired(), Email()],
        render_kw={"class": "form-control"}
    )

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')