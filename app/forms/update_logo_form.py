from flask_wtf import FlaskForm
from wtforms import FileField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import ValidationError
from werkzeug.datastructures import FileStorage

class UpdateLogoForm(FlaskForm):
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
            field.data.seek(0)
