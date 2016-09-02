from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import verify_password, User, Temp, generate_reset_password_confirmation_token, encrypt_passowrd, \
    generate_change_email_confirmation_token
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm, \
    ChangeEmailForm
from pymongo import MongoClient
from ..email import send_email
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from bson.objectid import ObjectId
import time
from datetime import datetime


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.activate \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.activate:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = MongoClient().blog.User.find_one({'email': form.email.data})
        if user is not None and verify_password(user.get('password'), form.password.data):
            user = Temp(id=user.get('_id'), username=user.get('username'), email=user.get('email'),
                        password=user.get('password'), activate=user.get('activate'), role=user.get('role'),
                        name=user.get('name'),
                        location=user.get('location'), about_me=user.get('about_me'), last_since=user.get('last_since'),
                        member_since=user.get('member_since'))
            login_user(user, form.remember_me.data)
            MongoClient().blog.User.update({'email': form.email.data}, {'$set': {'last_since': datetime.utcnow()}})
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
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
        User(email=form.email.data,
             username=form.username.data,
             password=form.password.data,
             name=form.name.data,
             location=form.location.data,
             about_me=form.about_me.data).new_user()
        user = MongoClient().blog.User.find_one({'email': form.email.data})
        temp = Temp(id=user.get('_id'), username=user.get('username'), email=user.get('email'),
                    password=user.get('password'), activate=False, role=user.get('role'), name=user.get('name'),
                    location=user.get('location'), about_me=user.get('about_me'), last_since=user.get('last_since'),
                    member_since=user.get('member_since'))
        token = temp.generate_confirmation_token
        send_email(temp.email, 'Confirm Your Account',
                   'auth/temp/confirm', user=temp, token=token)
        flash('A confirmation temp has been sent to you by temp.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        s.loads(token)
    except BadSignature:
        return render_template('Link_expired.html')
    data = s.loads(token)
    id = data.get('confirm')
    user = MongoClient().blog.User.find_one({'_id': ObjectId(id)})
    if user is None:
        flash('The confirmation link is invalid or has expired.')
    if user.get('activate'):
        flash('this Account is already confirm')
        return redirect(url_for('main.index'))
    MongoClient().blog.User.update({'_id': ObjectId(id)}, {'$set': {'activate': True}})
    time.sleep(1)
    flash('You have confirmed your account. Thanks!')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/temp/confirm', user=current_user, token=token)
    flash('A new confirmation temp has been sent to you by temp.')
    return redirect(url_for('main.index'))


@auth.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        token = generate_reset_password_confirmation_token(email=email)
        send_email(email, 'Reset Your Password',
                   'auth/temp/reset_password', token=token)
        flash('A reset password temp has been sent to you by temp.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        s.loads(token)
    except BadSignature:
        return render_template('Link_expired.html')
    data = s.loads(token)
    email = data.get('password_reset')
    user = MongoClient().blog.User.find_one({'temp': email})
    if user is None:
        flash('The confirmation link is invalid or has expired.')
        time.sleep(3)
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        password = encrypt_passowrd(form.password.data)
        MongoClient().blog.User.update({'temp': email}, {'$set': {'password': password}})
        flash('Change Success,you can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not verify_password(current_user.password_hash, form.old_password.data):
            flash('old password is not correct')
            form.data.clear()
        else:
            password = encrypt_passowrd(form.password.data)
            MongoClient().blog.User.update({'temp': current_user.email}, {'$set': {'password': password}})
            flash('Change Success,you can now login.')
            return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/change_email_request', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        MongoClient().blog.User.update({'temp': current_user.email}, {'$set': {'email_temp': email}})
        token = generate_change_email_confirmation_token(email=current_user.email)
        send_email(email, 'Reset Your Password',
                   'auth/temp/change_email', user=current_user, token=token)
        flash('A confirm temp has been sent to you by temp.')
        return redirect(url_for('main.index'))
    return render_template('auth/change_email_request.html', form=form)


@auth.route('/change_email/<token>', methods=['GET', 'POST'])
def change_email(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        s.loads(token)
    except BadSignature:
        return render_template('Link_expired.html')
    data = s.loads(token)
    email = data.get('change_email')
    email_temp = MongoClient().blog.User.find_one({'temp': email}).get('email_temp')
    MongoClient().blog.User.update({'temp': email}, {
        '$set': {'temp': email_temp}})
    MongoClient().blog.User.update({'temp': email_temp}, {'$unset': {'email_temp': email_temp}})
    logout_user()
    flash('Your e-mail successfully changed, please sign in again.')
    return redirect(url_for('auth.login'))
