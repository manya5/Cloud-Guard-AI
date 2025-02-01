from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField
)
from wtforms.validators import(
    Email,
    DataRequired,
    Length
)

class LoginForm(FlaskForm):
     email=StringField(
        'Enter your email',
        validators=[DataRequired(),Email()]
     )


     password=PasswordField(
         'Enter password',
         validators=[DataRequired(),Length(8)]
     )

     submit=SubmitField(
          'Login with Sky Vault',
    
     )


