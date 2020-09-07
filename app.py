from flask import Flask,render_template,flash,redirect,url_for,abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired
import click
import os
app = Flask(__name__) #定义flask的实例

##hahah
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret string')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SQLALCHEMY_COMMIT_TEARDOWN']=True
db = SQLAlchemy(app)

#Model
class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)

    # optional
    def __repr__(self):
        return '<Note %r>' % self.body

@app.shell_context_processor
def sehll_context():
    return {'db':db,'Note':Note}
#
@app.cli.command()
def init_db():
    db.create_all()
    click.echo("Initialized database.")
#
@app.cli.command()
def deinit_db():
    db.drop_all()

#form
class newNoteForm(FlaskForm):
    body=TextAreaField("Body",validators=[DataRequired()])
    submit=SubmitField("Save")

class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')

class EditNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')

@app.route("/new",methods=["GET","POST"])
def new_note():
    form=newNoteForm()
    if form.validate_on_submit():
        body=form.body.data
        note=Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        return redirect(url_for('index'))
    return render_template('new_note.html', form=form)

# @app.route('/delete')
@app.route('/index')
def index():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template('index.html', notes=notes, form=form)


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('Your note is updated.')
        return redirect(url_for('index'))
    form.body.data = note.body  # preset form input's value
    return render_template('edit_note.html', form=form)


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('Your note is deleted.')
    else:
        abort(400)
    return redirect(url_for('index'))


