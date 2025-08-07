import re
from typing import Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db

# CSRF Protection
csrf = CSRFProtect()

# Production-grade password validation regex
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

class LoginForm(FlaskForm):
    """Secure login form with CSRF protection"""
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RegistrationForm(FlaskForm):
    """Secure registration form with comprehensive validation"""
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('E-posta', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Şifre Onayı', validators=[
        DataRequired(), EqualTo('password', message='Şifreler eşleşmiyor.')
    ])
    first_name = StringField('Ad', validators=[Length(max=50)])
    last_name = StringField('Soyad', validators=[Length(max=50)])
    phone = StringField('Telefon', validators=[Length(max=20)])
    submit = SubmitField('Kayıt Ol')

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Production-grade password validation with specific security requirements
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(password, str) or len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır."
    
    if len(password) > 128:
        return False, "Şifre 128 karakterden uzun olamaz."
    
    if not re.search(r'[a-z]', password):
        return False, "Şifre en az bir küçük harf içermelidir."
    
    if not re.search(r'[A-Z]', password):
        return False, "Şifre en az bir büyük harf içermelidir."
    
    if not re.search(r'\d', password):
        return False, "Şifre en az bir rakam içermelidir."
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Şifre en az bir özel karakter (@$!%*?&) içermelidir."
    
    return True, ""

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Secure login with CSRF protection and comprehensive validation"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():  # This includes CSRF validation
        try:
            # Type-safe data extraction with None checks
            if not form.username.data or not form.password.data:
                flash('Kullanıcı adı ve şifre gereklidir.', 'error')
                return render_template('login.html', form=form)
                
            username_clean = form.username.data.strip().lower()
            password = form.password.data
            remember = form.remember.data
            
            # Enhanced user lookup with case-insensitive search
            user = User.query.filter_by(username=username_clean).first()
            
            if user and user.password_hash and check_password_hash(user.password_hash, password):
                if hasattr(user, 'is_active') and user.is_active:
                    try:
                        login_user(user, remember=remember)
                        
                        # Safe next page handling with validation
                        next_page: Optional[str] = request.args.get('next')
                        if next_page and not next_page.startswith(('http://', 'https://', '//')):
                            # Prevent open redirect vulnerabilities
                            display_name = user.first_name if hasattr(user, 'first_name') and user.first_name else user.username
                            flash(f'Hoş geldiniz, {display_name}!', 'success')
                            return redirect(next_page)
                        
                        display_name = user.first_name if hasattr(user, 'first_name') and user.first_name else user.username
                        flash(f'Hoş geldiniz, {display_name}!', 'success')
                        return redirect(url_for('main.dashboard'))
                    
                    except Exception as e:
                        current_app.logger.error(f"Login process error: {str(e)}")
                        flash('Giriş işlemi sırasında hata oluştu. Lütfen tekrar deneyin.', 'error')
                
                else:
                    flash('Hesabınız deaktive edilmiştir. Lütfen yönetici ile iletişime geçin.', 'error')
            else:
                # Generic error message to prevent username enumeration
                flash('Geçersiz kullanıcı adı veya şifre.', 'error')
                
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash('Giriş işlemi sırasında hata oluştu. Lütfen tekrar deneyin.', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Secure registration with production-grade validation and CSRF protection"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():  # This includes CSRF validation
        try:
            # Type-safe data extraction with comprehensive None checks
            if not form.username.data or not form.email.data or not form.password.data:
                flash('Kullanıcı adı, e-posta ve şifre gereklidir.', 'error')
                return render_template('register.html', form=form)
                
            # Extract and clean form data
            username_clean = form.username.data.strip().lower()
            email_clean = form.email.data.strip().lower()
            password = form.password.data
            first_name = form.first_name.data.strip() if form.first_name.data else None
            last_name = form.last_name.data.strip() if form.last_name.data else None
            phone = form.phone.data.strip() if form.phone.data else None
            
            # Production-grade password strength validation
            is_valid_password, password_error = validate_password_strength(password)
            if not is_valid_password:
                flash(password_error, 'error')
                return render_template('register.html', form=form)
            
            # Enhanced duplicate user validation with database integrity
            try:
                existing_user = User.query.filter(
                    (User.username == username_clean) | (User.email == email_clean)
                ).first()
                
                if existing_user:
                    if existing_user.username == username_clean:
                        flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
                    else:
                        flash('Bu e-posta adresi zaten kayıtlı.', 'error')
                    return render_template('register.html', form=form)
                    
            except Exception as db_error:
                current_app.logger.error(f"Database query error during registration: {str(db_error)}")
                flash('Kayıt kontrolü sırasında hata oluştu. Lütfen tekrar deneyin.', 'error')
                return render_template('register.html', form=form)
            
            # Create new user with comprehensive input sanitization
            try:
                user = User(
                    username=username_clean,
                    email=email_clean,
                    password_hash=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    is_active=True  # Default to active
                )
                
                db.session.add(user)
                db.session.commit()
                
                current_app.logger.info(f"New user registered: {username_clean}")
                flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as create_error:
                db.session.rollback()
                current_app.logger.error(f"User creation error: {str(create_error)}")
                flash('Kayıt sırasında hata oluştu. Lütfen tekrar deneyin.', 'error')
                return render_template('register.html', form=form)
                
        except Exception as e:
            current_app.logger.error(f"Registration process error: {str(e)}")
            flash('Kayıt işlemi sırasında beklenmeyen hata oluştu.', 'error')
            return render_template('register.html', form=form)
    
    # Handle form validation errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('register.html', form=form)
    
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
