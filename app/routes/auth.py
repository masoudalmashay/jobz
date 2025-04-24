import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from ..extensions import supabase, login_manager, s3
from werkzeug.utils import secure_filename
from gotrue.errors import AuthApiError
from flask_login import login_user, current_user, logout_user, login_required


from app.models.user import User
from app.forms.signup_form import SignupForm
from app.forms.login_form import LoginForm
from app.forms.reset_password import ResetPassword
from app.forms.update_password import UpdatePassword

import random
import string



auth = Blueprint("auth", __name__)




@auth.before_request
def clear_next_if_direct_access():
    if request.endpoint in ['auth.login', 'auth.register']:
        # Only clear if this isn't part of a redirect
        if not request.referrer or request.referrer == request.url:
            session['next'] = request.url




@auth.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = SignupForm()
    if form.validate_on_submit():
        company_name = form.company_name.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        logo = form.logo.data
        filename_original = secure_filename(logo.filename)

        only_filename, ext = os.path.splitext(filename_original)
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        filename = f"{only_filename}_{random_str}{ext}"


        try:

            
            response = supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"company_name": company_name,"email": email, "phone": phone,"logo_url": "", "email_confirmed": False}}})


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
            access_token = response.session.access_token
            refresh_token = response.session.refresh_token
            
            user = User(id=response.user.id, email=response.user.user_metadata['email'], email_verified=response.user.user_metadata['email_confirmed'], company_name=response.user.user_metadata['company_name'], phone=response.user.user_metadata['phone'], logo_url=response.user.user_metadata['logo_url'])
            
            session['supabase_access_token'] = access_token
            session['supabase_refresh_token'] = refresh_token

            login_user(user)



            supabase.auth.resend({
                "type": 'signup',
                "email": current_user.email
            })

            flash("🎉 تم تسجيل الدخول بنجاح", "success")

            next_page = session.get('next', url_for('profile.index'))
            return redirect(next_page or "/")
        except AuthApiError as e:
            if e.code == "user_already_exists":
                flash("📧 لديك حساب بهذا الإيميل", "warning")
            else:
                flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")
        except Exception as e:
            flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")

        

    
    
    return render_template('auth/register.html', form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        

        try:

            response = supabase.auth.sign_in_with_password({"email": email, "password": password})

            access_token = response.session.access_token
            refresh_token = response.session.refresh_token
            
            user = User(id=response.user.id, email=response.user.user_metadata['email'], email_verified=response.user.user_metadata['email_confirmed'], company_name=response.user.user_metadata['company_name'], phone=response.user.user_metadata['phone'], logo_url=response.user.user_metadata['logo_url'])
            
            session['supabase_access_token'] = access_token
            session['supabase_refresh_token'] = refresh_token

            
            login_user(user)
            

            flash("🎉 تم تسجيل الدخول بنجاح", "success")
            
            next_page = session['next'] or url_for('profile.index')

            
            return redirect(next_page)
            
        except AuthApiError as e:
            if e.code == "invalid_credentials":
                flash("🔒 تحقق من كلمة المرور أو البريد الإلكتروني", "error")
            else:
                flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")


        except Exception as e:
            flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")

    
    return render_template("auth/login.html", form=form)



@auth.route("/resend-verify-link")
def resend_verify_link():

    if current_user.is_authenticated:
        try:
            response = supabase.auth.resend({
            "type": 'email',
            "email": current_user.email
        })
        except AuthApiError as e:
            print(e)
    flash("🔍 قم بالتحقق من بريدك الإلكتروني", "info")
    return redirect(request.referrer or '/')

@auth.route("/verify-email")
def verify_email():
    # check the otp here
    if current_user.is_authenticated:
        response = supabase.auth.update_user({
            "data": {"email_confirmed": True}
        })

        flash('🎉 تم تأكيد الحساب بنجاح', 'success')
        return redirect(url_for('/'))
    
    flash('🚪 قم بتسجيل الدخول أولاً', 'warning')
    return redirect(url_for('/'))

    

@auth.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = ResetPassword()
    if form.validate_on_submit():
        try:
            email = form.email.data
            data = supabase.auth.reset_password_for_email(email, {})

            flash("🔗 لقد تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك", "info")
            return redirect(request.referrer or '/')
        except AuthApiError as e:
            flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")


    return render_template("auth/reset-password.html", form=form)


@auth.route("/confirm-update-password", methods=["GET", "POST"])
def confirm_update_password():

    try:
        response = supabase.auth.verify_otp(
        {
            "token_hash": request.args.get("access_token"), 
            "type": "email",
        }
        )

        access_token = response.session.access_token
        refresh_token = response.session.refresh_token
        
        user = User(id=response.user.id, email=response.user.user_metadata['email'], email_verified=response.user.user_metadata['email_confirmed'], company_name=response.user.user_metadata['company_name'], phone=response.user.user_metadata['phone'], logo_url=response.user.user_metadata['logo_url'])
        session['supabase_access_token'] = access_token
        session['supabase_refresh_token'] = refresh_token

        login_user(user)

        flash("🎉 يرجى تغيير كلمة السر", "success")


        return redirect(url_for('auth.update_password'))
    except:
        flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")

        return redirect(url_for('main.home')), 400


@auth.route("/update-password", methods=["GET", "POST"])
@login_required
def update_password():
    form = UpdatePassword()
    if form.validate_on_submit():
        password = form.password.data

        data = supabase.auth.update_user({
            "password": password
        })



        flash('🎉 تم تغيير كلمة السر بنجاح', "success")
        return redirect(url_for('main.home'))
    

    return render_template('auth/update-password.html', form=form)
    


@auth.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("auth.login"))

@login_manager.user_loader
def load_user(user_id):
    access_token = session.get('supabase_access_token')
    refresh_token = session.get('supabase_refresh_token')
    print(f'from load_user {refresh_token}')
    if access_token:
        try:
            supabase.auth.set_session(access_token=access_token, refresh_token=refresh_token)
            response = supabase.auth.get_user()
            if response and response.user:
                return User(id=response.user.id, email=response.user.user_metadata['email'], email_verified=response.user.user_metadata['email_confirmed'], company_name=response.user.user_metadata['company_name'], phone=response.user.user_metadata['phone'], logo_url=response.user.user_metadata['logo_url'])
        except AuthApiError as e:
            print(f"Access token expired or invalid: {e}")
            if refresh_token:
                
                try:
                    refresh_response = supabase.auth.refresh_session(refresh_token)
                    if refresh_response and refresh_response.session and refresh_response.session.access_token and refresh_response.session.refresh_token and refresh_response.user:
                        session['supabase_access_token'] = refresh_response.session.access_token
                        session['supabase_refresh_token'] = refresh_response.session.refresh_token
                        return User(id=response.user.id, email=response.user.user_metadata['email'], email_verified=response.user.user_metadata['email_confirmed'], company_name=response.user.user_metadata['company_name'], phone=response.user.user_metadata['phone'], logo_url=response.user.user_metadata['logo_url'])
                    else:
                        print(f"Token refresh failed: {refresh_response.error if refresh_response and hasattr(refresh_response, 'error') else 'Unknown refresh error'}")
                        session.pop('supabase_access_token', None)
                        session.pop('supabase_refresh_token', None)
                        return None
                except AuthApiError as refresh_e:
                    print(f"Refresh token also invalid: {refresh_e}")
                    session.pop('supabase_access_token', None)
                    session.pop('supabase_refresh_token', None)
                    return None
                except Exception as refresh_e:
                    print(f"Error during token refresh: {refresh_e}")
                    session.pop('supabase_access_token', None)
                    session.pop('supabase_refresh_token', None)
                    return None
            else:
                print("No refresh token available.")
                session.pop('supabase_access_token', None)
                return None
        except Exception as e:
            print(f"Error loading user from Supabase: {e}")
    return None