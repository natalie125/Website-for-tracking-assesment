from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    deadline = db.Column(db.Date)
    module_code = db.Column(db.String(50))
    status = db.Column(db.Boolean, default=False)
    intro = db.Column(db.String(100))


# with app.app_context():
#     db.create_all()

class CreateForm(FlaskForm):
    title = StringField(label="title", validators=[DataRequired("Title cannot be empty")])
    deadline = DateField(label="deadline", validators=[DataRequired("Deadline cannot be empty")])
    module_code = StringField(label="module_code", validators=[DataRequired("Module Code cannot be empty")])
    intro = StringField(label="intro", validators=[DataRequired("Introduction cannot be empty")])
    submit = SubmitField(label="submit")


@app.route('/')
def show_all():  # put application's code here
    return render_template("AllAssessments.html", assessments=Assessment.query.all())


@app.route('/create', methods=['GET', 'POST'])
def create_assessment():
    form = CreateForm()
    if form.validate_on_submit():
        title = form.title.data
        deadline = form.deadline.data
        module_code = form.module_code.data
        intro = form.intro.data
        assessment = Assessment(title=title, deadline=deadline, module_code=module_code, intro=intro)
        db.session.add(assessment)
        db.session.commit()
        return redirect("/")
    return render_template("CreateAssessment.html", form=form)


@app.route('/completed')
def completed_assessments():
    return render_template("CompletedAssessments.html",
                           assessments=Assessment.query.filter(Assessment.status == True).all())


@app.route('/uncompleted', methods=['GET', 'POST'])
def uncompleted_assessments():
    if request.method == 'POST':
        id = request.form['id']
        assessment = Assessment.query.get(id)
        if not assessment:
            flash("Not found")
        else:
            assessment.status = True
            try:
                db.session.merge(assessment)
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
    return render_template("UncompletedAssessments.html",
                           assessments=Assessment.query.filter(Assessment.status == False).all())



if __name__ == '__main__':
    app.run()
