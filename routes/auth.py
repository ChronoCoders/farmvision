from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                flash(f'Hoş geldiniz, {user.first_name or user.username}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash('Hesabınız deaktive edilmiştir. Lütfen yönetici ile iletişime geçin.', 'error')
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Tüm zorunlu alanları doldurun.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Şifreler eşleşmiyor.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kayıtlı.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Kayıt sırasında hata oluştu. Lütfen tekrar deneyin.', 'error')
            app.logger.error(f"Registration error: {str(e)}")
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        new_email = request.form.get('email', current_user.email)
        current_user.phone = request.form.get('phone', current_user.phone)
        
        # Fix: Check the NEW email, not current user's email
        if new_email != current_user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.', 'error')
                return render_template('profile.html')
        
        current_user.email = new_email
        
        # Password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        
        if current_password and new_password:
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Mevcut şifre yanlış.', 'error')
                return render_template('profile.html')
            
            if new_password != confirm_new_password:
                flash('Yeni şifreler eşleşmiyor.', 'error')
                return render_template('profile.html')
            
            if len(new_password) < 6:
                flash('Yeni şifre en az 6 karakter olmalıdır.', 'error')
                return render_template('profile.html')
            
            current_user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash('Profil bilgileriniz güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Profil güncellenirken hata oluştu.', 'error')
            app.logger.error(f"Profile update error: {str(e)}")
    
    return render_template('profile.html')
