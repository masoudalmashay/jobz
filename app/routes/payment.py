
from flask import Blueprint, request, session, render_template, url_for, flash, redirect

from flask_login import login_required, current_user

from ..extensions import supabase, supabase_admin, send_slack_notification

from app.forms.job_form import JobForm
from app.forms.payment_option_form import PaymentOptionForm
from app.forms.redeem_form import RedeemForm

from app.models.order import Order
from app.models.package import Package

from datetime import datetime

from app.extensions import db

import os
import requests
import dotenv
dotenv.load_dotenv()

payment = Blueprint("payment", __name__)


@payment.before_request
def redirect_if_not_authenticated():
    if request.endpoint == 'payment.checkout' and not current_user.is_authenticated:
        session['next'] = request.url



@payment.route('/package/<int:package_id>/', methods=["GET", "POST"])
@login_required
def checkout(package_id):
    package = Package.query.get_or_404(package_id)
    old_balance = current_user.balance

    if request.method == "POST":
        # Check if user has enough wallet balance
        if current_user.balance >= package.price:
            
            try:
                print('hi')
                # Fetch balance from Supabase
                sb_user = supabase.auth.get_user().user
                balance = sb_user.user_metadata.get("balance", 0)

                print(f"Current user: {sb_user}")

                if balance < package.price:
                    flash("رصيد المحفظة غير كافي لدفع هذه الباقة.", "error")

                    user_identifier = current_user.email if current_user.is_authenticated else "visitor"
                    send_slack_notification(f"A user tried to purchase but the balance {balance} and the package price {package.price} by {user_identifier}")

                    return redirect(url_for("payment.checkout", package_id=package.id))

                # Stage order in DB (not committed yet)
                new_order = Order(
                    user_id=current_user.id,
                    package_id=package.id,
                    post_limit=package.post_count,
                    posts_used=0,
                    purchased_at=datetime.utcnow(),
                    expires_at=None
                )
                db.session.add(new_order)
                db.session.flush()  

                # Deduct in Supabase
                new_balance = balance - package.price
                supabase.auth.update_user(
                    {"data": {"balance": new_balance}}
                )


                current_user.balance = new_balance  

                # If Supabase update worked → commit DB
                db.session.commit()

                flash("تم شراء الباقة بنجاح!", "success")

                user_identifier = current_user.email if current_user.is_authenticated else "visitor"
                send_slack_notification(f"A package {package.name} was purchased by {user_identifier}")

                return redirect(url_for("profile.wallet"))

            except Exception as e:
                # Rollback on fails
                db.session.rollback()
                current_user.balance = old_balance
                flash("حدث خطأ أثناء الدفع. لم يتم الخصم من رصيدك.", "error")

                user_identifier = current_user.email if current_user.is_authenticated else "visitor"
                send_slack_notification(f"An error caused by {user_identifier} -> {str(e)}")

                print(e)
                return redirect(url_for("payment.checkout", package_id=package.id))

        else:
            flash("رصيد المحفظة غير كافي لدفع هذه الباقة.", "error")

            user_identifier = current_user.email if current_user.is_authenticated else "visitor"
            send_slack_notification(f"A trial purchase but no sufficent balance by {user_identifier}")

            return redirect(url_for("payment.checkout", package_id=package.id))

    return render_template("payments/checkout.html", package=package)


@payment.route('/payment-options/', methods=["GET", "POST"])
@login_required
def payment_options():
    # package = Package.query.get_or_404(package_id)
    form = PaymentOptionForm()
    
    # if request.method == "GET":
    #     form.package_id.data = package.id

    if form.validate_on_submit():
        # session['package_id'] = form.package_id.data


        if form.payment_method.data == "prepaid":
            return redirect(url_for("payment.redeem_card"))
        else:
            flash("طريقة الدفع غير معروفة", "danger")
            return redirect(request.url or '/prices')

    return render_template("payments/payment_options.html", form=form)



# payment options 

# prepaid cards redeem option

def redeem_code(code):

    payload = {
        "code": code
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('Platform_API_KEY')}"
    }

    response = requests.post(f"{os.environ.get('VOUCHER_URL')}/redeem", json=payload, headers=headers)

    if response.status_code == 201:
        
        print(f"Code: {response.json()}")
        return {"status": True, "data": response.json()}
    else:
        print(f"🚨 Failed to redeem code: {response.status_code} - {response.text}")
        return {"status": False, "error": response.json()}
            


@payment.route("/redeem/", methods=["GET", "POST"])
@login_required
def redeem_card():
    form = RedeemForm()
    if form.validate_on_submit():
        code = form.code.data
        # package_id = session['package_id']

        if not code:
            flash("يرجى إدخال الكود 🧸", "error")
            return redirect(url_for("payments.redeem_card"))

        result = redeem_code(code)



        if result['status']:
            try:
                current_user.balance = float(current_user.balance) + float(result['data']['voucher']['voucher']['amount'])
                print(f"New balance: {result}")
                response = supabase.auth.update_user({
                    "data": {"balance": current_user.balance}
                })
            except (KeyError, ValueError):
                flash("حدث خطأ أثناء استرداد الرمز. يرجى المحاولة مرة أخرى. 🐣", "error")

                user_identifier = current_user.email if current_user.is_authenticated else "visitor"
                send_slack_notification(f"A redeemed failed error caused by {user_identifier} -> {str(result)}")

                return redirect(url_for("payment.redeem_card"))

            flash("✅ تم التعبئة بنجاح", "success")
            session["is_party"] = True

            user_identifier = current_user.email if current_user.is_authenticated else "visitor"
            send_slack_notification(f"A code redeemed successfully by {user_identifier}")

            return redirect(url_for("profile.wallet"))

        else:
            flash("الرمز غير صالح أو تم استخدامه من قبل 🐣", "error")

            user_identifier = current_user.email if current_user.is_authenticated else "visitor"
            send_slack_notification(f"A used or wrong code used by {user_identifier}")


    return render_template("payments/redeem.html", form=form)






# TODO: Impelement the payment for packages from local wallet balance
@payment.route('/purchase/redeem/success', methods=["GET", "POST"])
@login_required
def redeem_success():


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


# OnePay payment option

