
from flask import Blueprint, request, session, render_template, url_for, flash, redirect

from flask_login import login_required, current_user

from app.forms.job_form import JobForm
from app.forms.payment_option_form import PaymentOptionForm
from app.forms.redeem_form import RedeemForm

from app.models.order import Order
from app.models.package import Package

from datetime import datetime

from app.extensions import db

payment = Blueprint("payment", __name__)


@payment.before_request
def redirect_if_not_authenticated():
    if request.endpoint == 'payment.payment_options' and not current_user.is_authenticated:
        session['next'] = request.url



@payment.route('/payment-options/<int:package_id>', methods=["GET", "POST"])
@login_required
def payment_options(package_id):
    package = Package.query.get_or_404(package_id)
    form = PaymentOptionForm()
    
    if request.method == "GET":
        form.package_id.data = package.id

    if form.validate_on_submit():
        session['package_id'] = form.package_id.data


        if form.payment_method.data == "prepaid":
            return redirect(url_for("payment.redeem_card"))
        else:
            flash("طريقة الدفع غير معروفة", "danger")
            return redirect(request.url or '/prices')

    return render_template("payments/payment_options.html", form=form, package=package)



# payment options 

# prepaid cards redeem option

def verify_card_with_provider(code, package_id):
    # Call the provider's API with the code
    # Example (replace with actual HTTP request to their API):
    
    # Example response
    if code == "12345":
        return {
            "status": "valid",           # or "invalid"
            "package_id": package_id             # ID of the associated package
        }
    
    return {
            "status": "invalid",           # or "invalid"
            "package_id": package_id              # ID of the associated package
        }
    


@payment.route("/redeem/", methods=["GET", "POST"])
@login_required
def redeem_card():
    form = RedeemForm()
    if form.validate_on_submit():
        code = form.code.data
        package_id = session['package_id']

        if not code:
            flash("يرجى إدخال الكود 🧸", "error")
            return redirect(url_for("payments.redeem_card"))

        # Validate code with provider API
        response = verify_card_with_provider(code, package_id)



        if response['status'] == "valid":
            package = Package.query.get(response['package_id'])

            # Save to session to allow going to /success
            session['valid_code'] = code
            session['package_id'] = package.id

            return redirect(url_for("payment.redeem_success"))

        else:
            flash("الرمز غير صالح أو تم استخدامه من قبل 🐣", "error")


    return render_template("payments/redeem.html", form=form)







@payment.route('/purchase/redeem/success', methods=["GET", "POST"])
@login_required
def redeem_success():
    code = session.get('valid_code')
    package_id = session.get('package_id')

    if not code or not package_id:
        flash("لم تقم بإدخال رمز صالح", "warning")
        return redirect(url_for("payments.redeem_card"))

    # ✅ Re-validate the code with the provider
    provider_response = verify_card_with_provider(code, package_id)

    if provider_response["status"] != "valid" or provider_response["package_id"] != package_id:
        flash("رمز غير صالح أو تم استخدامه", "error")
        return redirect(url_for("payments.redeem_card"))

    # Continue as safe
    package = Package.query.get(package_id)

    new_order = Order(
        user_id=current_user.id,
        package_id=package.id,
        post_limit=package.post_count,
        posts_used=0,
        purchased_at=datetime.utcnow(),
        expires_at=None
    )

    db.session.add(new_order)
    db.session.commit()

    # 🔐 Optionally tell provider that the code was redeemed, to prevent re-use
    # mark_code_as_used_with_provider(code)

    # Clear session
    session.pop('valid_code', None)
    session.pop('package_id', None)

    flash("تم تفعيل الرمز بنجاح، يمكنك الآن إضافة وظيفة", "success")
    return redirect(url_for("job_listing.add"))


# onePay payment option

