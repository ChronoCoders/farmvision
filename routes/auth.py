from typing import Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
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
        # Type-safe input extraction with validation
        username: Optional[str] = request.form.get('username')
        password: Optional[str] = request.form.get('password')
        remember: bool = bool(request.form.get('remember'))
        
        # Comprehensive None and empty string validation
        if not username or not username.strip():
            flash('Kullanıcı adı gereklidir.', 'error')
            return render_template('login.html')
            
        if not password or not password.strip():
            flash('Şifre gereklidir.', 'error')
            return render_template('login.html')
        
        username_clean = username.strip()
        user = User.query.filter_by(username=username_clean).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user, remember=remember)
                next_page: Optional[str] = request.args.get('next')
                display_name = user.first_name if user.first_name else user.username
                flash(f'Hoş geldiniz, {display_name}!', 'success')
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
        # Type-safe form input extraction with proper validation
        username: Optional[str] = request.form.get('username')
        email: Optional[str] = request.form.get('email')
        password: Optional[str] = request.form.get('password')
        confirm_password: Optional[str] = request.form.get('confirm_password')
        first_name: Optional[str] = request.form.get('first_name')
        last_name: Optional[str] = request.form.get('last_name')
        phone: Optional[str] = request.form.get('phone')
        
        # Comprehensive input validation with None checks
        if not username or not username.strip():
            flash('Kullanıcı adı gereklidir.', 'error')
            return render_template('register.html')
            
        if not email or not email.strip():
            flash('E-posta adresi gereklidir.', 'error')
            return render_template('register.html')
            
        if not password or not password.strip():
            flash('Şifre gereklidir.', 'error')
            return render_template('register.html')
            
        if not confirm_password or not confirm_password.strip():
            flash('Şifre onayı gereklidir.', 'error')
            return render_template('register.html')
        
        # Validate password strength
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Şifreler eşleşmiyor.', 'error')
            return render_template('register.html')
        
        # Additional validation with proper None handling
        username_clean = username.strip()
        email_clean = email.strip()
        
        # Check for valid email format (basic validation)
        if '@' not in email_clean or len(email_clean.split('@')) != 2:
            flash('Geçerli bir e-posta adresi girin.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username_clean).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email_clean).first():
            flash('Bu e-posta adresi zaten kayıtlı.', 'error')
            return render_template('register.html')
        
        # Create new user with validated inputs
        user = User(
            username=username_clean,
            email=email_clean,
            password_hash=generate_password_hash(password),
            first_name=first_name.strip() if first_name else None,
            last_name=last_name.strip() if last_name else None,
            phone=phone.strip() if phone else None
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Kayıt sırasında hata oluştu. Lütfen tekrar deneyin.', 'error')
            current_app.logger.error(f"Registration error: {str(e)}")
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
        # Type-safe form input with proper validation
        first_name: Optional[str] = request.form.get('first_name')
        last_name: Optional[str] = request.form.get('last_name')
        new_email: Optional[str] = request.form.get('email')
        phone: Optional[str] = request.form.get('phone')
        
        # Validate and sanitize inputs
        if first_name is not None:
            current_user.first_name = first_name.strip() if first_name.strip() else None
            
        if last_name is not None:
            current_user.last_name = last_name.strip() if last_name.strip() else None
            
        if phone is not None:
            current_user.phone = phone.strip() if phone.strip() else None
        
        # Email validation with None check
        if new_email and new_email.strip():
            new_email_clean = new_email.strip()
            # Basic email format validation
            if '@' not in new_email_clean or len(new_email_clean.split('@')) != 2:
                flash('Geçerli bir e-posta adresi girin.', 'error')
                return render_template('profile.html')
            
            # Check if email is already in use by another user
            if new_email_clean != current_user.email:
                existing_user = User.query.filter_by(email=new_email_clean).first()
                if existing_user and existing_user.id != current_user.id:
                    flash('Bu e-posta adresi zaten başka bir kullanıcı tarafından kullanılıyor.', 'error')
                    return render_template('profile.html')
            
            current_user.email = new_email_clean
        
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
            current_app.logger.error(f"Profile update error: {str(e)}")
    
    return render_template('profile.html')
