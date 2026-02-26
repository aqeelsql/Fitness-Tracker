from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'fitness_tracker_secret_2023'

DATABASE = 'workouts.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    # Workouts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_title TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            duration INTEGER NOT NULL,
            calories_burned INTEGER NOT NULL,
            workout_date DATE NOT NULL,
            status TEXT DEFAULT 'Pending Review',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Goals table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_title TEXT NOT NULL,
            goal_type TEXT NOT NULL,
            target_value INTEGER NOT NULL,
            current_value INTEGER DEFAULT 0,
            target_date DATE NOT NULL,
            status TEXT DEFAULT 'In Progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Achievements table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            badge_icon TEXT NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('coach_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== FRONT STAGE ====================
@app.route('/', methods=['GET', 'POST'])
def front_stage():
    conn = get_db()
    
    if request.method == 'POST':
        title = request.form.get('workout_title')
        workout_type = request.form.get('workout_type')
        duration = request.form.get('duration')
        calories = request.form.get('calories_burned')
        workout_date = request.form.get('workout_date')
        notes = request.form.get('notes', '')
        
        if title and workout_type and duration and calories and workout_date:
            conn.execute('''
                INSERT INTO workouts (workout_title, workout_type, duration, calories_burned, workout_date, notes) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, workout_type, int(duration), int(calories), workout_date, notes))
            conn.commit()
            flash("Your workout has been logged. Keep moving!", 'success')
            conn.close()
            return redirect(url_for('front_stage'))
    
    # Get quick stats for homepage
    stats = {
        'total_workouts': conn.execute('SELECT COUNT(*) FROM workouts').fetchone()[0],
        'total_calories': conn.execute('SELECT COALESCE(SUM(calories_burned), 0) FROM workouts').fetchone()[0],
        'total_minutes': conn.execute('SELECT COALESCE(SUM(duration), 0) FROM workouts').fetchone()[0],
        'recent_workouts': conn.execute('SELECT * FROM workouts ORDER BY workout_date DESC LIMIT 5').fetchall()
    }
    conn.close()
    
    return render_template('front_stage.html', stats=stats)

# ==================== WORKOUT HISTORY ====================
@app.route('/history')
def workout_history():
    conn = get_db()
    
    # Get filter parameters
    workout_type = request.args.get('type', '')
    status = request.args.get('status', '')
    date_from = request.args.get('from', '')
    date_to = request.args.get('to', '')
    
    query = 'SELECT * FROM workouts WHERE 1=1'
    params = []
    
    if workout_type:
        query += ' AND workout_type = ?'
        params.append(workout_type)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if date_from:
        query += ' AND workout_date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND workout_date <= ?'
        params.append(date_to)
    
    query += ' ORDER BY workout_date DESC'
    
    workouts = conn.execute(query, params).fetchall()
    
    # Get unique workout types for filter dropdown
    workout_types = conn.execute('SELECT DISTINCT workout_type FROM workouts').fetchall()
    
    conn.close()
    
    return render_template('workout_history.html', 
                         workouts=workouts, 
                         workout_types=workout_types,
                         filters={'type': workout_type, 'status': status, 'from': date_from, 'to': date_to})

# ==================== ANALYTICS ====================
@app.route('/analytics')
def analytics():
    conn = get_db()
    
    # Overall statistics
    stats = {
        'total_workouts': conn.execute('SELECT COUNT(*) FROM workouts').fetchone()[0],
        'total_calories': conn.execute('SELECT COALESCE(SUM(calories_burned), 0) FROM workouts').fetchone()[0],
        'total_minutes': conn.execute('SELECT COALESCE(SUM(duration), 0) FROM workouts').fetchone()[0],
        'avg_duration': conn.execute('SELECT COALESCE(AVG(duration), 0) FROM workouts').fetchone()[0],
        'avg_calories': conn.execute('SELECT COALESCE(AVG(calories_burned), 0) FROM workouts').fetchone()[0],
    }
    
    # Workouts by type
    workouts_by_type = conn.execute('''
        SELECT workout_type, COUNT(*) as count, SUM(duration) as total_duration, SUM(calories_burned) as total_calories
        FROM workouts 
        GROUP BY workout_type
    ''').fetchall()
    
    # Workouts by status
    workouts_by_status = conn.execute('''
        SELECT status, COUNT(*) as count 
        FROM workouts 
        GROUP BY status
    ''').fetchall()
    
    # Weekly progress (last 7 days)
    weekly_data = conn.execute('''
        SELECT workout_date, COUNT(*) as count, SUM(duration) as duration, SUM(calories_burned) as calories
        FROM workouts 
        WHERE workout_date >= date('now', '-7 days')
        GROUP BY workout_date
        ORDER BY workout_date
    ''').fetchall()
    
    # Monthly progress (last 30 days)
    monthly_data = conn.execute('''
        SELECT strftime('%Y-%m-%d', workout_date) as date, COUNT(*) as count, SUM(calories_burned) as calories
        FROM workouts 
        WHERE workout_date >= date('now', '-30 days')
        GROUP BY strftime('%Y-%m-%d', workout_date)
        ORDER BY date
    ''').fetchall()
    
    # Best workout day
    best_day = conn.execute('''
        SELECT workout_date, SUM(calories_burned) as total_calories
        FROM workouts
        GROUP BY workout_date
        ORDER BY total_calories DESC
        LIMIT 1
    ''').fetchone()
    
    conn.close()
    
    return render_template('analytics.html', 
                         stats=stats, 
                         workouts_by_type=workouts_by_type,
                         workouts_by_status=workouts_by_status,
                         weekly_data=weekly_data,
                         monthly_data=monthly_data,
                         best_day=best_day)

# ==================== GOALS ====================
@app.route('/goals')
def goals():
    conn = get_db()
    
    # Get all goals
    all_goals = conn.execute('SELECT * FROM goals ORDER BY target_date ASC').fetchall()
    
    # Update goal progress automatically
    for goal in all_goals:
        if goal['goal_type'] == 'Total Workouts':
            current = conn.execute('SELECT COUNT(*) FROM workouts').fetchone()[0]
        elif goal['goal_type'] == 'Total Calories':
            current = conn.execute('SELECT COALESCE(SUM(calories_burned), 0) FROM workouts').fetchone()[0]
        elif goal['goal_type'] == 'Total Minutes':
            current = conn.execute('SELECT COALESCE(SUM(duration), 0) FROM workouts').fetchone()[0]
        else:
            current = goal['current_value']
        
        # Update progress
        conn.execute('UPDATE goals SET current_value = ? WHERE id = ?', (current, goal['id']))
        
        # Check if goal is achieved
        if current >= goal['target_value'] and goal['status'] != 'Achieved':
            conn.execute('UPDATE goals SET status = ? WHERE id = ?', ('Achieved', goal['id']))
    
    conn.commit()
    
    # Refresh goals after update
    goals_list = conn.execute('SELECT * FROM goals ORDER BY target_date ASC').fetchall()
    
    # Statistics
    stats = {
        'total_goals': len(goals_list),
        'achieved': len([g for g in goals_list if g['status'] == 'Achieved']),
        'in_progress': len([g for g in goals_list if g['status'] == 'In Progress'])
    }
    
    conn.close()
    
    return render_template('goals.html', goals=goals_list, stats=stats)

@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    if request.method == 'POST':
        title = request.form.get('goal_title')
        goal_type = request.form.get('goal_type')
        target_value = request.form.get('target_value')
        target_date = request.form.get('target_date')
        
        if title and goal_type and target_value and target_date:
            conn = get_db()
            conn.execute('''
                INSERT INTO goals (goal_title, goal_type, target_value, target_date) 
                VALUES (?, ?, ?, ?)
            ''', (title, goal_type, int(target_value), target_date))
            conn.commit()
            conn.close()
            flash('Goal added successfully! Let\'s crush it!', 'success')
            return redirect(url_for('goals'))
    
    return render_template('add_goal.html')

@app.route('/delete_goal/<int:goal_id>')
def delete_goal(goal_id):
    conn = get_db()
    conn.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
    conn.commit()
    conn.close()
    flash('Goal removed.', 'success')
    return redirect(url_for('goals'))

# ==================== COACH'S CORNER ====================
@app.route('/coach_login', methods=['GET', 'POST'])
def coach_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'fit_guru2023':
            session['logged_in'] = True
            return redirect(url_for('fitness_dashboard'))
        else:
            flash('Access denied. Invalid credentials.', 'error')
    
    return render_template('coach_login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('front_stage'))

# ==================== FITNESS DASHBOARD ====================
@app.route('/fitness_dashboard')
def fitness_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('coach_login'))
    
    conn = get_db()
    workouts = conn.execute('SELECT * FROM workouts ORDER BY workout_date DESC').fetchall()
    conn.close()
    
    return render_template('fitness_dashboard.html', workouts=workouts)

@app.route('/edit_workout/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    if not session.get('logged_in'):
        return redirect(url_for('coach_login'))
    
    conn = get_db()
    
    if request.method == 'POST':
        title = request.form.get('workout_title')
        workout_type = request.form.get('workout_type')
        duration = request.form.get('duration')
        calories = request.form.get('calories_burned')
        workout_date = request.form.get('workout_date')
        status = request.form.get('status')
        
        conn.execute('''
            UPDATE workouts 
            SET workout_title = ?, workout_type = ?, duration = ?, 
                calories_burned = ?, workout_date = ?, status = ?
            WHERE id = ?
        ''', (title, workout_type, int(duration), int(calories), workout_date, status, workout_id))
        conn.commit()
        conn.close()
        flash('Workout updated successfully!', 'success')
        return redirect(url_for('fitness_dashboard'))
    
    workout = conn.execute('SELECT * FROM workouts WHERE id = ?', (workout_id,)).fetchone()
    conn.close()
    
    if not workout:
        flash('Workout not found.', 'error')
        return redirect(url_for('fitness_dashboard'))
    
    return render_template('edit_workout.html', workout=workout)

@app.route('/delete_workout/<int:workout_id>')
def delete_workout(workout_id):
    if not session.get('logged_in'):
        return redirect(url_for('coach_login'))
    
    conn = get_db()
    conn.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))
    conn.commit()
    conn.close()
    
    flash('Workout deleted successfully.', 'success')
    return redirect(url_for('fitness_dashboard'))

@app.route('/assign_workout', methods=['GET', 'POST'])
def assign_workout():
    if not session.get('logged_in'):
        return redirect(url_for('coach_login'))
    
    if request.method == 'POST':
        title = request.form.get('workout_title')
        workout_type = request.form.get('workout_type')
        duration = request.form.get('duration')
        calories = request.form.get('calories_burned')
        workout_date = request.form.get('workout_date')
        status = request.form.get('status', 'Pending Review')
        
        if title and workout_type and duration and calories and workout_date:
            conn = get_db()
            conn.execute('''
                INSERT INTO workouts (workout_title, workout_type, duration, calories_burned, workout_date, status) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, workout_type, int(duration), int(calories), workout_date, status))
            conn.commit()
            conn.close()
            flash('New workout plan assigned successfully!', 'success')
            return redirect(url_for('fitness_dashboard'))
    
    return render_template('assign_workout.html')

if __name__ == '__main__':
    # Use port 5000 for local testing, change to 80 for EC2 deployment with sudo
    app.run(host='0.0.0.0', port=5000, debug=True)
