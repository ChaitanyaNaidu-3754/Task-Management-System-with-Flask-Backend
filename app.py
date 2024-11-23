from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

IST = timezone(timedelta(hours=5, minutes=30))

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String(200), nullable = False)
    desc = db.Column(db.String(500), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now(IST))

    def __repr__(self)  -> str:
        return f"{self.sno} - {self.title}"

class Done(db.Model):
    sno = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String(200), nullable = False)
    desc = db.Column(db.String(500), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now(IST))
    completed_on = db.Column(db.DateTime, default = datetime.now(IST))

    def __repr__(self)  -> str:
        return f"{self.sno} - {self.title}"
    
with app.app_context():
    db.create_all()
    print("Database created!")

@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/done', methods=['GET'])
def done():
    done_tasks = Done.query.all()
    return render_template('done.html', done_tasks=done_tasks)

@app.route('/done/<int:sno>', methods=['POST'])
def handle_done_task_action(sno):
    todo = Todo.query.get_or_404(sno)  # Fetch the todo by its sno
    
    # Check which action is being requested (done or delete)
    action = request.form.get('action')

    if action == 'mark_done':
        # Create a Done task based on the Todo task
        done_task = Done(
            title=todo.title,
            desc=todo.desc,
            date_created = todo.date_created,
            completed_on=datetime.now(IST)  # Set the completed date
        )
        
        # Add to Done table and remove from Todo table
        db.session.add(done_task)
        db.session.delete(todo)
        db.session.commit()

    elif action == 'delete':
        # Just delete the Todo task without marking it as done
        db.session.delete(todo)
        db.session.commit()

    return redirect(url_for('index'))  # Redirect back to the index page


@app.route('/delete_task/<int:sno>', methods=['POST'])
def delete_permanent(sno):
    done = Done.query.get_or_404(sno)
    action = request.form.get('action')
    if action == 'delete':
        # Delete the task without Permanently
        db.session.delete(done)
        db.session.commit()
    return redirect(url_for('done'))

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        title = request.form['title']  # Get 'title' from the form
        desc = request.form['desc']    # Get 'desc' from the form
        date_created = datetime.now(IST)
        
        # Create a new Todo instance and add it to the database
        todo = Todo(title=title, desc=desc, date_created=date_created)
        db.session.add(todo)
        db.session.commit()

        return redirect(url_for('index'))  # Redirect back to the index page

    return render_template('index.html')   

if __name__ == "__main__":
    app.run(debug=True, port=8000)