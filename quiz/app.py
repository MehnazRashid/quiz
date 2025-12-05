from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Store exams in memory (for demo purposes)
exams = {}

def parse_questions(questions_text):
    """Parse questions text with strict formatting (no space after question number)"""
    questions = []
    current_question = None
    question_count = 0
    
    for line in questions_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check for question line (format "1.Question text")
        parts = line.split('.', 1)
        if len(parts) == 2 and parts[0].isdigit():
            question_count += 1
            if current_question:
                questions.append(current_question)
            current_question = {
                'number': parts[0],
                'text': parts[1].strip(),
                'options': []
            }
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            if current_question:
                current_question['options'].append(line)
    
    if current_question:
        questions.append(current_question)
    
    return questions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=['GET', 'POST'])
def input_method():
    if request.method == 'POST':
        session['input_method'] = request.form.get('input_method')
        return redirect(url_for('input_details'))
    return render_template('input.html')

@app.route('/input-details', methods=['GET', 'POST'])
def input_details():
    if request.method == 'POST':
        session['topic_or_material'] = request.form.get('topic_or_material')
        session['mcq_count'] = int(request.form.get('mcq_count', 10))
        return redirect(url_for('show_prompt'))
    return render_template('input_details.html')

@app.route('/prompt')
def show_prompt():
    prompt_text = f"""Generate exactly {session['mcq_count']} multiple-choice questions about "{session['topic_or_material']}".

Strict formatting requirements:
1. List each question with exactly 4 options (A, B, C, D)
2. Number each question sequentially with NO space after the number (e.g., "1.")
3. Put the correct answer for all questions at the end under "Answers:" 
4. Each answer must be on its own line with just the letter (A-D)
5. Format exactly like this example:

1.What is the capital of France?
A) London
B) Paris
C) Berlin
D) Madrid

2.Which planet is known as the Red Planet?
A) Venus
B) Mars
C) Jupiter
D) Saturn

Answers:
B
B"""
    
    return render_template('prompt.html', prompt_text=prompt_text)

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'POST':
        exam_id = len(exams) + 1
        questions_text = request.form.get('questions')
        answers_text = request.form.get('answers')
        
        questions_list = parse_questions(questions_text)
        answers_list = [a.strip().upper() for a in answers_text.split('\n') if a.strip()]
        
        exams[exam_id] = {
            'questions': questions_list,
            'answers': answers_list
        }
        
        session['exam_id'] = exam_id
        return render_template('exam.html', 
                             questions=questions_list,
                             exam_id=exam_id)
    
    return redirect(url_for('index'))

@app.route('/submit-exam/<int:exam_id>', methods=['POST'])
def submit_exam(exam_id):
    if exam_id not in exams:
        return redirect(url_for('index'))
    
    user_answers = []
    exam_questions = exams[exam_id]['questions']
    for question in exam_questions:
        answer = request.form.get(f'q{question["number"]}')
        if answer:
            user_answers.append(answer.upper())
    
    correct_answers = exams[exam_id]['answers']
    score = 0
    results = []
    
    for i in range(len(correct_answers)):
        if i < len(user_answers) and user_answers[i] == correct_answers[i]:
            score += 1
            results.append(True)
        else:
            results.append(False)
    
    return render_template('results.html',
                         score=score,
                         total=len(correct_answers),
                         results=results,
                         questions=exam_questions,
                         correct_answers=correct_answers,
                         user_answers=user_answers)

if __name__ == '__main__':
    app.run(debug=True)