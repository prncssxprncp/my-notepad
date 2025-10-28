from flask import Blueprint, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

# Create blueprint
main_bp = Blueprint('main', __name__, template_folder='templates')

# Database
db = SQLAlchemy()

# DATABASE MODEL
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    archived = db.Column(db.Boolean, default=False)

# BLUEPRINT INITIALIZATION

@main_bp.record_once
def on_load(state):
    """Initialize DB once the blueprint is registered."""
    db.init_app(state.app)
    with state.app.app_context():
        db.create_all()


# -------------------------------
# ROUTES
# -------------------------------

# Home - Active Notes
@main_bp.route('/')
def home():
    notes = Note.query.filter_by(archived=False).all()
    return render_template('home.html', notes=notes)


# Add new note
@main_bp.route('/add', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']
    new_note = Note(title=title, content=content)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('main.home'))


# Archive (move to archive)
@main_bp.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.archived = True
    db.session.commit()
    return redirect(url_for('main.home'))


# Archive page
@main_bp.route('/archive')
def archive():
    archived_notes = Note.query.filter_by(archived=True).all()
    return render_template('archive.html', archived_notes=archived_notes)


# Restore a note
@main_bp.route('/restore/<int:note_id>', methods=['POST'])
def restore_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.archived = False
    db.session.commit()
    return redirect(url_for('main.archive'))


# Permanently delete a note
@main_bp.route('/permanent_delete/<int:note_id>', methods=['POST'])
def permanent_delete(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('main.archive'))
