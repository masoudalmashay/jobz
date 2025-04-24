from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class RedeemForm(FlaskForm):
    code = StringField(
        'كود الكرت',
        validators=[
            InputRequired(message="يرجى إدخال  الكود"),
        ]
    )

    
