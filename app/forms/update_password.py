from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import InputRequired, Length, EqualTo

class UpdatePassword(FlaskForm):
    

    password = PasswordField(
        'كلمة المرور',
        validators=[
            InputRequired(message="يرجى إدخال كلمة المرور"),
            Length(min=6, message="يجب أن تكون كلمة المرور 6 أحرف على الأقل")
        ]
    )

    confirm_password = PasswordField(
        'تأكيد كلمة المرور',
        validators=[
            InputRequired(message="يرجى تأكيد كلمة المرور"),
            EqualTo('password', message="كلمتا المرور غير متطابقتين")
        ]
    )

    
