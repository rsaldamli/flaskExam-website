from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
db = SQLAlchemy(app)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    session['score'] = 0
    return render_template('index.html')


# @app.route('/start', methods=['GET', 'POST'])
# def start():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect(url_for('quiz'))
#     return render_template('start.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        session['score'] = 0  # Reset the current score to 0
        return redirect(url_for('quiz'))
    return render_template('start.html')


@app.route('/quiz')
def quiz():
    questions = Question.query.all()
    return render_template('quiz.html', questions=questions, enumerate=enumerate)


@app.route('/delete_highscore', methods=['POST'])
def delete_highscore():
    # Find the highest score entry
    highscore_entry = Score.query.order_by(Score.score.desc()).first()
    if highscore_entry:
        db.session.delete(highscore_entry)
        db.session.commit()

    # After deletion, update the highscore in the session
    new_highscore_entry = Score.query.order_by(Score.score.desc()).first()
    if new_highscore_entry:
        session['highscore'] = new_highscore_entry.score
    else:
        session['highscore'] = 0  # No scores left, set highscore to 0

    return redirect(url_for('index'))


@app.route('/result', methods=['POST'])
def result():
    questions = Question.query.all()
    score = 0
    for i, question in enumerate(questions):
        if request.form.get(f'question-{i}') == question.answer:
            score += 1

    session['score'] = score
    highscore_entry = Score.query.order_by(Score.score.desc()).first()
    highscore = highscore_entry.score if highscore_entry else 0

    if score > highscore:
        session['highscore'] = score
        new_score = Score(score=score)
        db.session.add(new_score)
        db.session.commit()
    else:
        session['highscore'] = highscore

    return render_template('result.html', score=score, highscore=session['highscore'])


@app.route('/about')
def about():
    return render_template('about.html')


# Admin Panel for adding questions
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        question_text = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        new_question = Question(
            question=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            answer=answer
        )

        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('admin'))

    questions = Question.query.all()
    return render_template('admin.html', questions=questions)


@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
