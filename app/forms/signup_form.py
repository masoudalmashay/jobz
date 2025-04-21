from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField
from wtforms.validators import InputRequired, Length, EqualTo, Regexp, Email
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import ValidationError
from werkzeug.datastructures import FileStorage

class SignupForm(FlaskForm):
    email = StringField(
        'البريد الإلكتروني',
        validators=[
            InputRequired(message="يرجى إدخال البريد الإلكتروني"),
            Email(message="يرجى إدخال بريد إلكتروني صالح"),
            Length(min=5, max=50, message="يجب أن يكون البريد الإلكتروني بين 5 و 50 حرفًا")
        ]
    )

    phone = StringField(
    'رقم الهاتف',
    validators=[
        InputRequired(message="يرجى إدخال رقم الهاتف"),
        Regexp(
            r'^(091|092|093|094)[0-9]{7}$',
            message="رقم الهاتف غير صالح (يجب أن يبدأ بـ 091 أو 092 أو 093 أو 094 ويتبعه 7 أرقام)"
        )
    ]
    )

    company_name = StringField(
        'اسم الشركة',
        validators=[
            InputRequired(message="يرجى إدخال اسم الشركة"),
            Length(min=2, max=100, message="يجب أن يكون اسم الشركة بين 2 و 100 حرف")
        ]
    )

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

    logo = FileField(
        'شعار الشركة',
        validators=[
            FileRequired(message="يرجى رفع شعار الشركة"),
            FileAllowed(['jpg', 'jpeg', 'png'], message="يسمح فقط بصيغ PNG أو JPG أو JPEG")
        ]
    )

    def validate_logo(form, field: FileField):
        if field.data and isinstance(field.data, FileStorage):
            if len(field.data.read()) > 1 * 1024 * 1024:  # 1MB
                raise ValidationError("حجم الملف يجب ألا يتجاوز 1 ميجابايت")
            field.data.seek(0)  # Reset read pointer
