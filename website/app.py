from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'a1837370b18bfb0690d391d9a4054fc8985c10ae88e0ebb364b0ae9595bea63f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Person(db.Model):
    __tablename__ = 'Person'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    Grades = db.relationship('Grades', backref='person', lazy=True)
    feedback = db.relationship('Feedback', backref='instructor', lazy=True)
    remarkereqs = db.relationship('RemarkRequests', backref='remarks', lazy=True)

class Grades(db.Model):
    __tablename__ = 'Grades'
    grade_id = db.Column(db.Integer, db.ForeignKey('Person.id'), primary_key=True, nullable=False)
    lab1 = db.Column(db.Integer, nullable=True)
    lab2 = db.Column(db.Integer, nullable=True)
    lab3 = db.Column(db.Integer, nullable=True)

    assign1 = db.Column(db.Integer, nullable=True)
    assign2 = db.Column(db.Integer, nullable=True)
    assign3 = db.Column(db.Integer, nullable=True)

    midterm= db.Column(db.Integer, nullable=True)
    exam = db.Column(db.Integer, nullable=True)


class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('Person.id'), nullable=False)
    feedback1 = db.Column(db.String(100), nullable=True)
    feedback2= db.Column(db.String(100), nullable=True)
    feedback3 = db.Column(db.String(100), nullable=True)
    feedback4 = db.Column(db.String(100), nullable=True)
    feedback_status = db.Column(db.String(10), nullable=False, default = 'open')



class RemarkRequests(db.Model):
    __tablename__ = 'RemarkRequests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Person.id'), nullable=False)
    case_name = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Approved, Rejected

@app.route('/')
@app.route('/home')
def home():
    if 'username' not in session:
        flash('Please Login')
        return redirect(url_for('login'))
    pagename = 'home'
    return render_template('index.html', pagename=pagename)

@app.route('/lectureNotes')
def lectureNotes():
    if 'username' not in session:
        flash('Please Login')
        return redirect(url_for('login'))
    pagename = 'lectureNotes'
    return render_template('lec_notes.html', pagename=pagename)


@app.route('/assignments')
def assignment():
    if 'username' not in session:
        flash('Please Login')
        return redirect(url_for('login'))
    pagename = 'assignments'
    return render_template('assignments.html', pagename=pagename)

@app.route('/labs')
def labs():
    if 'username' not in session:
        flash('Please Login')
        return redirect(url_for('login'))
    pagename = 'labs'
    return render_template('labs.html', pagename=pagename)

@app.route('/team')
def team():
    if 'username' not in session:
        flash('Please Login')
        return redirect(url_for('login'))
    pagename = 'team'
    return render_template('team.html', pagename=pagename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        user_name = request.form['Username']
        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        user_type = request.form['user_type']

        check_duplicate = Person.query.filter_by(username=user_name).first()
        if check_duplicate:
            flash('Username already exists')
            return render_template('register.html')

        reg_details = (user_name, hashed_password, user_type)
        add_users(reg_details)
        flash('Registration successful! Please login now:')
        return redirect(url_for('login'))

def add_users(reg_details):
    user = Person(username=reg_details[0], password=reg_details[1], type=reg_details[2])
    db.session.add(user)
    db.session.commit()
    if user.type == 'student':
        #create blank entry in grades
        user_id = user.id
        blank_grades = Grades(grade_id = user_id)
        db.session.add(blank_grades)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'username' in session:
            flash('You are already logged in!')
            return redirect(url_for('home'))
        return render_template('login.html')
    else:
        username = request.form['Username']
        password = request.form['Password']
        print(username)
        person = Person.query.filter_by(username=username).first()

        if not person or not bcrypt.check_password_hash(person.password, password):
            flash('Please check your login details and try again.', 'error')
            return render_template('login.html')

        session['username'] = username  #declare session username and type
        session['type'] = person.type
        session.permanent = True

        if session['type'] == 'student':
            flash("Welcome " + username + ", click to see your current grades.")
        else:
            flash("Welcome instructor " + username + ", click to see all the grades of your class.")

        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', default=None)
    session.pop('type', default=None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' in session and session['type'] == 'student':
        if request.method == 'GET':
            allinstructors = Person.query.filter_by(type='instructor').all()
            return render_template('feedback.html',  instructors = allinstructors)
        else:
            print(request.form)
            feedback_details= (
                request.form['instructor_id'],
                request.form['feedback1'],
                request.form['feedback2'],
                request.form['feedback3'],
                request.form['feedback4'],
            )
            feedback = Feedback(instructor_id = feedback_details[0], feedback1 = feedback_details[1], feedback2 = feedback_details[2], feedback3 = feedback_details[3], feedback4 = feedback_details[4])
            db.session.add(feedback)
            db.session.commit()
            flash('Your feedback has been submitted successfully')
            return render_template('feedback.html')
        
    if 'username' in session and session['type'] == 'instructor':
        if request.method == 'GET':
            instructor = Person.query.filter_by(username=session['username']).first()
            allfeedback = Feedback.query.filter_by(instructor_id = instructor.id).all()
            return render_template('feedback.html', feedbacks=allfeedback)
        
        else:
            feedback_details= (
                request.form['feedback_id'],
                request.form['status'],
            )
            feedbackform = Feedback.query.filter_by(id = feedback_details[0]).first()
            feedbackform.feedback_status = feedback_details[1]
            db.session.commit()
            return redirect(url_for('feedback'))
        
    flash('Please Login')
    return redirect(url_for('login'))

@app.route('/grades', methods=['GET', 'POST'])
def grades():
    if 'username' in session:
        username = session['username']

    if session['type'] == 'student':
        if request.method == 'GET':
            student = Person.query.filter_by(username=username).first() #return one student tuple
            grades = Grades.query.filter_by(grade_id=student.id).first() #return one student grades
            remarkreqs = RemarkRequests.query.filter_by(student_id = student.id).all()
            return render_template('grades.html', grades=grades, remarkrequests = remarkreqs, username=username)
        else:
            student = Person.query.filter_by(username=username).first() #return one student tuplet
            assignment = request.form['assignment']
            reason = request.form['reason']

            exist = RemarkRequests.query.filter_by(student_id=student.id, case_name=assignment).first()
            if exist:
                flash("You have already submitted a remark request!")
            else:
                remarkrequest = RemarkRequests(student_id=student.id, case_name=assignment, reason=reason, status='Pending')
                db.session.add(remarkrequest)
                db.session.commit()
                flash("Remark request submitted successfully!")
            return redirect(url_for('grades'))

    if session['type'] == 'instructor':
        if request.method == 'GET':
            all_grades = []
            students = Person.query.filter_by(type='student').all() #all students
            for student in students:
                student_grade = Grades.query.filter_by(grade_id=student.id).first()
                if student_grade:
                    all_grades.append({
                        'username': student.username,
                        'grades': student_grade
                    })
            remarkreqs = RemarkRequests.query.all()
            return render_template('grades.html', grades=all_grades, remarkrequests = remarkreqs, username=username)
        else:
            student_name = request.form['student']
            assignment = request.form['assignment']
            status = request.form['status']

            student = Person.query.filter_by(username=student_name).first() 
            if student:
                remarkreq = RemarkRequests.query.filter_by(student_id = student.id, case_name = assignment).first()
                if remarkreq:
                    remarkreq.status = status
                    db.session.commit()
                    flash('Remark request status updated')
                else:
                    flash('Not found')
            else:
                flash('Not found student')
            return redirect(url_for('grades'))    
    
    flash('Please Login')
    return redirect(url_for('login'))

@app.route('/entermarks', methods=['GET', 'POST'])
def entermarks():
    if 'username' in session and session['type'] == 'instructor':
        if request.method == 'GET':
            students = Person.query.filter_by(type = 'student').all()
            assignments = ['lab1', 'lab2', 'lab3', 'assign1', 'assign2', 'assign3', 'midterm', 'exam']
            return render_template('entermarks.html', students = students, assignments = assignments)
        
        else:
            username = request.form['student_username']
            assignment = request.form['assignment']
            new_mark = request.form['mark']
        
            student = Person.query.filter_by(username = username, type='student').first()
            studentgrade = Grades.query.filter_by(grade_id = student.id).first()
            if not studentgrade:
                studentgrade = Grades(grade_id = student.id)
                db.session.add(studentgrade)

            if assignment == 'lab1':
                studentgrade.lab1 = new_mark
            elif assignment == 'lab2':
                studentgrade.lab2 = new_mark
            elif assignment == 'lab3':
                studentgrade.lab3 = new_mark
            elif assignment == 'assign1':
                studentgrade.assign1 = new_mark
            elif assignment == 'assign2':
                studentgrade.assign2 = new_mark
            elif assignment == 'assign3':
                studentgrade.assign3 = new_mark
            elif assignment == 'midterm':
                studentgrade.midterm = new_mark
            elif assignment == 'exam':
                studentgrade.exam = new_mark

            db.session.commit()
            flash('Marks updated successfully!')
            return redirect(url_for('grades'))
        
    flash('Please Login')
    return redirect(url_for('login'))

@app.route('/remarks', methods=['GET', 'POST'])
def remarks():
    if 'username' in session and session['type'] == 'instructor':
        if request.method == 'GET':
            remark_requests = RemarkRequests.query.all()
            return render_template('remarks.html', remarks=remark_requests)
        else:
            remark_id = request.form['remark_id']
            new_status = request.form['status']
            remark = RemarkRequests.query.filter_by(id=remark_id).first()
            if remark:
                remark.status = new_status
                db.session.commit()
                flash("Remark request status updated successfully")
                return redirect(url_for('remarks'))
            else:
                flash("Remark request failed")
            
            return redirct(url_for('remarks'))
    flash('Please Login')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Person.query.first():
            hashed_password_1 = bcrypt.generate_password_hash('student1').decode('utf-8')
            student1 = Person(username='student1', password=hashed_password_1, type='student')

            hashed_password_2 = bcrypt.generate_password_hash('student2').decode('utf-8')
            student2 = Person(username='student2', password=hashed_password_2, type='student')

            hashed_password_3 = bcrypt.generate_password_hash('instructor1').decode('utf-8')
            instructor1 = Person(username='instructor1', password=hashed_password_3, type='instructor')

            hashed_password_4 = bcrypt.generate_password_hash('instructor2').decode('utf-8')
            instructor2 = Person(username='instructor2', password=hashed_password_4, type='instructor')

            db.session.add_all([student1, student2, instructor1, instructor2])
            db.session.commit()
        
        if not Grades.query.first():
            grade1 = Grades(grade_id=1, lab1=90, lab2=95, lab3=85, assign1=86, assign2=90, assign3=98, midterm=90, exam=78)
            grade2 = Grades(grade_id=2, lab1=95, lab2=90, lab3=80, assign1=80, assign2=90, assign3=90, midterm=85, exam=80)

            db.session.add_all([grade1, grade2])
            db.session.commit()
        
        if not Feedback.query.first():
            instructor1 = Person.query.filter_by(username='instructor1').first()
            instructor2 = Person.query.filter_by(username='instructor2').first()
            feedback1 = Feedback(instructor_id=instructor1.id, feedback1="Great Teaching", feedback2="Need more examples for practice", feedback3="nice pace", feedback4="slides are effective")
            feedback2 = Feedback(instructor_id=instructor2.id, feedback1="Great ", feedback2="Need more examples", feedback3="good pace", feedback4="slides are effective")
            
            db.session.add_all([feedback1, feedback2])
            db.session.commit()
            
        db.session.close()
    
    app.run(debug=True)
