from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length
from app.models.city import City
from app.models.category import Category
from flask_login import current_user

class JobForm(FlaskForm):
    title = StringField(
        'عنوان الوظيفة',
        validators=[
            DataRequired(message='هذا الحقل مطلوب'),
            Length(max=255, message='العنوان طويل جدًا')
        ]
    )
    
    description = TextAreaField(
        'الوصف',
        validators=[
            DataRequired(message='الرجاء إدخال وصف للوظيفة')
        ]
    )
    
    category_id = SelectField(
        'التصنيف',
        coerce=int,
        validators=[
            DataRequired(message='الرجاء اختيار تصنيف')
        ]
    )

    city_id = SelectField(
        'المدينة',
        coerce=int,
        validators=[
            DataRequired(message='الرجاء اختيار مدينة')
        ]
    )

    user_id = HiddenField(
        validators=[
            DataRequired(message='المستخدم غير معروف')
        ]
    )

    def set_choices(self):
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
        self.city_id.choices = [(c.id, c.name) for c in City.query.all()]

    def user_id(self):
        self.user_id = current_user.id
