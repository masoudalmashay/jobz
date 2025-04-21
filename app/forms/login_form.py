from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            InputRequired(message="يرجى إدخال البريد الإلكتروني"),
            Email(message="يرجى إدخال بريد إلكتروني صالح"),
            Length(min=5, max=50, message="يجب أن يكون البريد الإلكتروني بين 5 و 50 حرفًا")
        ]
    )

    password = PasswordField(
        'كلمة المرور',
        validators=[
            InputRequired(message="يرجى إدخال كلمة المرور"),
            Length(min=6, message="يجب أن تكون كلمة المرور 6 أحرف على الأقل")
        ]
    )
