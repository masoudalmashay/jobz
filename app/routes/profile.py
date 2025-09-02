from flask import request, flash, redirect, url_for, render_template, Blueprint
from flask_login import login_required, current_user
from app.forms.update_info_form import UpdateInfoForm
from app.forms.update_logo_form import UpdateLogoForm
from app.forms.update_password import UpdatePassword

import random
import string

from werkzeug.utils import secure_filename

from app.extensions import s3, supabase, db

import os

profile = Blueprint('profile', __name__)


@profile.route('/', methods=['GET', 'POST'])
@login_required
def edit():
    print(current_user.logo_url)
    logo_form = UpdateLogoForm(obj=current_user)
    info_form = UpdateInfoForm(obj=current_user)
    password_form = UpdatePassword()

    if 'submit_logo' in request.form and logo_form.validate_on_submit():
        logo = logo_form.logo.data
        filename_original = secure_filename(logo.filename)

        only_filename, ext = os.path.splitext(filename_original)
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        filename = f"{only_filename}_{random_str}{ext}"

        try:
            s3.upload_fileobj(
                logo,
                os.getenv("R2_BUCKET"),
                filename,
                ExtraArgs={'ACL': 'public-read'}
            )

            logo_url = f"{filename}"

            supabase.auth.update_user({
                "data": {"logo_url": logo_url}
            })

            current_user.logo_url = logo_url


            flash("🎨 تم تحديث الشعار بنجاح", "success")


        except:
            flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")


        

    elif 'submit_info' in request.form and info_form.validate_on_submit():
        phone = info_form.phone.data
        company_name = info_form.company_name.data
        
        try:
            response = supabase.auth.update_user({
                "data": {"company_name": company_name, "phone": phone}
            })

            current_user.phone = phone
            current_user.company_name = company_name

            flash("🎉 تم تحديث البيانات بنجاح", "success")
        except Exception as e:
            flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")


        

    elif 'submit_password' in request.form and password_form.validate_on_submit():
        try:
            password = password_form.password.data

            response = supabase.auth.update_user({
            "password": password
            })

            flash('🎉 تم تغيير كلمة السر بنجاح', "success")
        except:
            flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")



    return render_template(
        'profile/edit.html',
        logo_form=logo_form,
        info_form=info_form,
        password_form=password_form
    )


@profile.route('/wallet', methods=['GET'])
@login_required
def wallet():
    
    return render_template(
        'profile/wallet.html',
        balance=current_user.balance
    )
