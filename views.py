from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import create_note, get_notes, find_note, update_note, soft_delete, restore, permanent_delete, find_user, update_user, get_notes as _get_notes
from datetime import datetime, timedelta
from functools import wraps # Import the wraps module
import random

main_bp = Blueprint('main', __name__)

# Ginawa nating mas maayos at malinis ang login_required
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user'): 
            flash('Login required','warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

# --- 1. HOME Route (Filters Active Notes) ---
@main_bp.route('/')
@login_required
def home():
    username = session.get('user')
    # Tama na ang filtering logic para lang sa 'active' notes ng user.
    notes = [n for n in _get_notes() if n.get('owner') == username and n.get('status') == 'active']
    # Nagre-resolve sa TypeError/Empty response.
    return render_template('home.html', notes=notes)

# --- 2. ARCHIVE Route (MISSING ROUTE: Ito ang kailangan mong idagdag) ---
@main_bp.route('/archive')
@login_required
def archive():
    username = session.get('user')
    # FIX: Filtering logic para lang sa 'archived' notes ng user.
    archived_notes = [n for n in _get_notes() if n.get('owner') == username and n.get('status') == 'archived']
    # Ipinapasa ang data sa archive.html
    return render_template('archive.html', archived_notes=archived_notes)

# --- 3. ADD NOTE Route ---
@main_bp.route('/note/add', methods=['POST'])
@login_required
def add_note():
    title = request.form.get('title')
    content = request.form.get('content')
    if not title: flash('Title required','danger'); return redirect(url_for('main.home'))
    # Ang create_note ay nagse-set ng status='active'
    create_note(session.get('user'), title, content)
    flash('Note added','success')
    return redirect(url_for('main.home'))

# --- 4. DELETE/ARCHIVE Route (Pinagsama ang Archive at Permanent Delete) ---
@main_bp.route('/note/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = find_note(note_id) 
    
    if not note or note.get('owner') != session.get('user'):
        flash('Note not found or unauthorized.','danger')
        return redirect(url_for('main.home'))

    # Logic: Kapag active (galing sa home), i-archive. Kapag archived (galing sa archive), i-delete.
    if note.get('status') == 'active':
        soft_delete(note_id) # Nagse-set ng status='archived'
        flash('Note archived successfully!','info')
        return redirect(url_for('main.home'))
    
    elif note.get('status') == 'archived':
        permanent_delete(note_id) # Permanent deletion
        flash('Note permanently deleted.','warning')
        return redirect(url_for('main.archive'))
        
    return redirect(url_for('main.home'))

# --- 5. RESTORE Route (MISSING ROUTE: Ito ang kailangan mong idagdag) ---
@main_bp.route('/note/restore/<int:note_id>', methods=['POST'])
@login_required
def restore_note(note_id):
    note = find_note(note_id)
    
    if not note or note.get('owner') != session.get('user'):
        flash('Note not found or unauthorized.','danger')
        return redirect(url_for('main.archive'))
    
    restore(note_id) # Nagse-set ng status='active'
    flash('Note restored to active list!','success')
    return redirect(url_for('main.home'))

# --- 6. EDIT Route ---
@main_bp.route('/note/edit/<int:note_id>', methods=['GET','POST'])
@login_required
def edit_note(note_id):
    note = find_note(note_id)
    
    if not note or note.get('owner') != session.get('user'):
        flash('Note not found or unauthorized.','danger')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if not title: flash('Title required','danger'); return redirect(url_for('main.edit_note', note_id=note_id))
        update_note(note_id, {'title': title, 'content': content})
        flash('Note updated','success')
        return redirect(url_for('main.home'))
        
    # Ipinapasa ang data sa edit_note.html
    return render_template('edit_note.html', note=note)

# --- Profile Routes (Mula sa iyong views.py) ---
@main_bp.route('/profile')
@login_required
def profile():
    user = find_user(session.get('user'))
    return render_template('profile.html', user=user)

@main_bp.route('/profile/edit', methods=['GET','POST'])
@login_required
def edit_profile():
    # ... (Your existing edit_profile logic here) ...
    # Tiyakin na ang buong edit_profile function mo ay nakopya dito
    pass
    # return render_template('edit_profile.html', user=user)

# --- Profile OTP Logic (Kung ginagamit mo ito) ---
@main_bp.route('/profile/send-otp', methods=['POST'])
@login_required
def profile_send_otp():
    # ... (Your existing profile_send_otp logic here) ...
    pass
    # return redirect(url_for('main.edit_profile'))