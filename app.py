from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database
def init_db():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            vote1 TEXT NOT NULL,
            vote2 TEXT NOT NULL,
            vote3 TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS vote_count (
            group_name TEXT PRIMARY KEY,
            points_3 INTEGER DEFAULT 0,
            points_2 INTEGER DEFAULT 0,
            points_1 INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0
        )
    ''')
    # Initialize vote_count table with groups
    groups = [f'Group {i}' for i in range(1, 12)]
    for group in groups:
        c.execute('INSERT OR IGNORE INTO vote_count (group_name, points_3, points_2, points_1, total_points) VALUES (?, 0, 0, 0, 0)', (group,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    groups = [f'Group {i}' for i in range(1, 12)]
    return render_template('index.html', groups=groups)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    group_name = request.form['group_name']
    vote1 = request.form['vote1']
    vote2 = request.form['vote2']
    vote3 = request.form['vote3']

    if len(set([vote1, vote2, vote3])) != 3:
        flash("You must vote for three unique groups.")
        return redirect(url_for('index'))

    if group_name in [vote1, vote2, vote3]:
        flash("You cannot vote for your own group.")
        return redirect(url_for('index'))

    conn = sqlite3.connect('votes.db')
    c = conn.cursor()

    # Check if the group has already voted
    c.execute("SELECT * FROM votes WHERE group_name = ?", (group_name,))
    if c.fetchone():
        conn.close()
        flash("Your group has already voted.")
        return redirect(url_for('index'))

    c.execute("INSERT INTO votes (group_name, vote1, vote2, vote3) VALUES (?, ?, ?, ?)", (group_name, vote1, vote2, vote3))
    
    # Update vote_count table
    c.execute("UPDATE vote_count SET points_3 = points_3 + 1, total_points = total_points + 3 WHERE group_name = ?", (vote1,))
    c.execute("UPDATE vote_count SET points_2 = points_2 + 1, total_points = total_points + 2 WHERE group_name = ?", (vote2,))
    c.execute("UPDATE vote_count SET points_1 = points_1 + 1, total_points = total_points + 1 WHERE group_name = ?", (vote3,))

    conn.commit()
    conn.close()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return "Vote recorded successfully!"

@app.route('/results')
def results():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM vote_count ORDER BY total_points DESC")
    results = c.fetchall()
    conn.close()
    return render_template('results.html', results=results)

@app.route('/reset')
def reset():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute("DELETE FROM votes")
    c.execute("UPDATE vote_count SET points_3 = 0, points_2 = 0, points_1 = 0, total_points = 0")
    conn.commit()
    conn.close()
    flash("The votes have been reset.")
    return redirect(url_for('results'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

