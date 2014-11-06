from flask import render_template, redirect, request, url_for, flash,current_app
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User,get_user
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..api.user_api import validate_user,email_exists,username_exists,validate_user,change_user_password,insert_new_user
from ..funcsmodule import getUserDetails,getWebUID
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
@auth.before_app_request
def before_request():
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      
      
        user = get_user("email",form.email_or_username.data)
        if user is None:
            user = get_user("username",form.email_or_username.data)
            
               
                       
        if user and validate_user(user.username,form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        
        
        #check to see if user is in MLST database
        details = getUserDetails(form.email_or_username.data)
        if details:
            id =getWebUID(form.email_or_username.data,form.password.data)
            if id !=0:
                if username_exists(details['username']):
                    flash("You are already an MLST user but your username already exists -"
                          "Please enter new details")
                    return redirect(url_for('auth.register'))
                if email_exists(details['email']):
                    flash("You are already an MLST user but your email already exists -"
                          "Please enter new details")
                    return redirect(url_for('auth.register'))
                values = {
                    'username':details['username'],
                    'email':details['email'],
                    'password':form.password.data,
                    'firstname':details['firstname'],
                    'lastname':details['name'],
                    'department':details['dept'],
                    'institution':details['institution'],
                    'city':details['city'],
                    'country':details['country']                                  
                }
                id = insert_new_user(values)
                        
                s = Serializer(current_app.config['SECRET_KEY'], 3600)
                token = s.dumps({'confirm': id})        
                        
                send_email(details['email'], 'Confirm Your Account',
                                   'auth/email/confirm', user=details['username'], token=token)
                flash('Your details have been copied from MLST to Eneterobase. '
                      'A confirmation email has been sent to you by email.')
                return redirect(url_for('auth.login'))
            
        flash('Invalid username/email or password.') 
                
                
                         
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #username,email,password,firstname,lastname,department,institution,city,country
        
        values = {'username':form.username.data,
                  'email':form.email.data,
                  'password':form.password.data,
                  'firstname':form.firstname.data,
                  'lastname':form.lastname.data,
                  'department':form.department.data,
                  'institution':form.institution.data,
                  'city':form.city.data,
                  'country':form.country.data
                  }
                  
        id = insert_new_user(values)
        
        s = Serializer(current_app.config['SECRET_KEY'], 3600)
        token = s.dumps({'confirm': id})        
        
        send_email(form.email.data, 'Confirm Your Account',
                   'auth/email/confirm', user=form.username.data, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    print "in here"
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if validate_user(current_user.username,form.old_password.data):
            change_user_password(current_user.id,form.password.data)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = get_user("email", form.email.data)
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = get_user("email",form.email.data)
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if validate_user(current_user.username,form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
