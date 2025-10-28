from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import find_user, add_user, hash_password, verify_password, update_user
from datetime import datetime, timedelta
import random

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        # REQUIRED FIELDS (Updated to match 'name' attributes in register.html)
        required = [
            'first_name', 'last_name', 'date_of_birth', 'contact_number',
            'username', 'email', 'password', 'confirm_password',
            'city_municipality', 'barangay', 'zip_code' # Added address fields
        ]

        # 1. Check for missing fields
        for r in required:
            if not data.get(r):
                flash('Please fill all required fields.','danger')
                # Return form_data to retain user inputs in case of error
                return render_template('register.html', form_data=data)
        
        # 2. Password mismatch check
        if data.get('password') != data.get('confirm_password'):
            flash('Passwords do not match.','danger')
            return render_template('register.html', form_data=data)
        
        # 3. Username existence check
        if find_user(data.get('username')):
            flash('Username already exists.','danger')
            return render_template('register.html', form_data=data)
        
        # 4. Age/DOB validation and calculation
        dob_str = data.get('date_of_birth')
        try:
            dob = datetime.fromisoformat(dob_str)
        except ValueError:
            flash('Invalid date format.','danger')
            return render_template('register.html', form_data=data)
            
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Backend Age range check (18-100 based on register.html logic)
        if age < 18 or age > 100:
            flash('Must be between 18 and 100 years old to register.','danger')
            return render_template('register.html', form_data=data)

        # 5. Address Formation
        # Gagamitin ang mga hiwalay na field para mabuo ang isang 'address' string
        address_string = f"{data.get('barangay')}, {data.get('city_municipality')}, Laguna, {data.get('zip_code')}"

        # 6. Prepare user data for 'add_user' (Using the correct keys)
        user_to_add = {
            'first_name': data.get('first_name'),
            'middle_name': data.get('middle_name'),
            'last_name': data.get('last_name'),
            'dob': dob_str, 
            'age': age,
            'contact': data.get('contact_number'), 
            'address': address_string, 
            'username': data.get('username'),
            'email': data.get('email'),
            'password_hash': hash_password(data.get('password'))
        }
        
        # 7. Add user and REDIRECT TO LOGIN (as requested)
        add_user(user_to_add)
        flash('Registration successful! Please sign in.','success')
        return redirect(url_for('auth.login'))
        
    # Initial GET request
    return render_template('register.html', form_data={})


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # FIX: Kunin at i-strip ang whitespace
        u = request.form.get('username')
        p = request.form.get('password')
        
        username_input = u.strip() if u is not None else ''
        password_input = p.strip() if p is not None else ''

        user = find_user(username_input) # Gagamitin ang na-strip na username
        
        # Login success logic: checks user and verifies password, then redirects to home
        # Gagamitin ang na-strip na password para sa verification
        if user and verify_password(user.get('password_hash'), password_input):
            session.clear(); session['user'] = user['username']; flash('Logged in','success'); 
            return redirect(url_for('main.home')) # Redirect to home on success
            
        flash('Invalid credentials','danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear(); flash('Logged out','info'); return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        user = find_user(username)
        if not user: flash('Username not found','danger'); return render_template('forgot_password.html')
        otp = '{:06d}'.format(random.randint(0,999999))
        session['otp'] = otp; session['otp_user'] = username; session['otp_expires'] = (datetime.utcnow() + timedelta(minutes=3)).isoformat()
        flash(f'OTP (demo): {otp} — expires in 3 minutes','info'); return redirect(url_for('auth.verify_otp'))
    return render_template('forgot_password.html')

@auth_bp.route('/verify-otp', methods=['GET','POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp'); newp = request.form.get('password'); conf = request.form.get('confirm_password')
        if not (otp and newp and conf): flash('Fill all fields','danger'); return render_template('forgot_password.html')
        if newp != conf: flash('Passwords mismatch','danger'); return render_template('forgot_password.html')
        stored = session.get('otp'); usern = session.get('otp_user'); expires = session.get('otp_expires')
        if not stored or not usern or not expires: flash('Start forgot password again','danger'); return redirect(url_for('auth.forgot_password'))
        if datetime.utcnow() > datetime.fromisoformat(expires): flash('OTP expired','danger'); session.pop('otp',None); session.pop('otp_expires',None); return redirect(url_for('auth.forgot_password'))
        if otp != stored: flash('Invalid OTP','danger'); return render_template('forgot_password.html')
        update_user(usern, {'password_hash': hash_password(newp)})
        session.pop('otp',None); session.pop('otp_user',None); session.pop('otp_expires',None)
        flash('Password updated. Please login','success'); return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')