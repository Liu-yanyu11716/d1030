from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "diary.db"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 首頁：顯示日記列表與搜尋
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    query = "SELECT id, date, title FROM diary ORDER BY date DESC"
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        query = f"SELECT id, date, title FROM diary WHERE title LIKE '%{keyword}%' OR content LIKE '%{keyword}%' ORDER BY date DESC"

    c.execute(query)
    diaries = c.fetchall()
    conn.close()

    return render_template('index.html', diaries=diaries)

# 新增日記
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')
        title = request.form['title']
        content = request.form['content']

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO diary (date, title, content) VALUES (?, ?, ?)", (date, title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit.html', diary=None)

# 查看日記
@app.route('/view/<int:diary_id>')
def view(diary_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM diary WHERE id = ?", (diary_id,))
    diary = c.fetchone()
    conn.close()
    return render_template('view.html', diary=diary)

# 編輯日記
@app.route('/edit/<int:diary_id>', methods=['GET', 'POST'])
def edit(diary_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == 'POST':
        date = request.form['date']
        title = request.form['title']
        content = request.form['content']
        c.execute("UPDATE diary SET date=?, title=?, content=? WHERE id=?", (date, title, content, diary_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view', diary_id=diary_id))
    else:
        c.execute("SELECT * FROM diary WHERE id=?", (diary_id,))
        diary = c.fetchone()
        conn.close()
        return render_template('edit.html', diary=diary)

# 刪除日記
@app.route('/delete/<int:diary_id>')
def delete(diary_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM diary WHERE id=?", (diary_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
