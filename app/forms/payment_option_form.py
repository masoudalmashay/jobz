from flask_wtf import FlaskForm
from wtforms import HiddenField, RadioField, SubmitField
from wtforms.validators import DataRequired

class PaymentOptionForm(FlaskForm):
    package_id = HiddenField(validators=[DataRequired()])
    
    payment_method = RadioField(
        "طريقة الدفع",
        choices=[("prepaid", "كروت الدفع")],  # Add more as needed
        validators=[DataRequired(message="يرجى اختيار طريقة الدفع")]
    )
    
    submit = SubmitField("استمرار")

    def set_package_id(self, package_id):
        self.package_id = package_id
