from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length, Regexp, Email


class UpdateInfoForm(FlaskForm):
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            
        ]
    )
    phone = StringField(
        'رقم الهاتف',
        validators=[
            InputRequired(message="يرجى إدخال رقم الهاتف"),
            Regexp(r'^(091|092|093|094)[0-9]{7}$', message="رقم الهاتف غير صالح")
        ]
    )
    company_name = StringField(
        'اسم الشركة',
        validators=[
            InputRequired(),
            Length(min=2, max=100)
        ]
    )
