from ai_module import extract_obligations
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/contracts.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect('/dashboard')
        else:
            return "Invalid email or password"

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database/contracts.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('database/contracts.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM contracts")
    total_contracts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM obligations")
    total_obligations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM obligations WHERE risk_level='High'")
    high_risk = cursor.fetchone()[0]

    cursor.execute("""
        SELECT obligation_type, due_date, risk_level
        FROM obligations
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_obligations = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        total_contracts=total_contracts,
        total_obligations=total_obligations,
        high_risk=high_risk,
        recent_obligations=recent_obligations
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload_contract():

    if request.method == 'POST':

        contract_name = request.form['contract_name']
        contract_text = request.form['contract_text']

        conn = sqlite3.connect('database/contracts.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO contracts
            (contract_name, upload_date, contract_text)
            VALUES (?, datetime('now'), ?)
            """,
            (contract_name, contract_text)
        )

        contract_id = cursor.lastrowid

        extracted = extract_obligations(contract_text)

        for item in extracted:

            cursor.execute(
                """
                INSERT INTO obligations
                (
                    contract_id,
                    obligation_type,
                    due_date,
                    responsible_person,
                    clause_text,
                    risk_level,
                    summary
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contract_id,
                    item["type"],
                    item["due_date"],
                   item["responsible_person"],
                    contract_text,
                    item["risk"],
                    item["summary"]
                )
            )

            obligation_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO reminders
                (
                    obligation_id,
                    reminder_date,
                    status
                )
                VALUES (?, ?, ?)
                """,
                (
                    obligation_id,
                    item["due_date"],
                    "Pending"
                )
            )

        conn.commit()
        conn.close()

        return redirect('/obligations')

    return render_template('upload_contract.html')


@app.route('/obligations')
def obligations():

    conn = sqlite3.connect('database/contracts.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT obligation_type,
           due_date,
           responsible_person,
           risk_level,
           summary
    FROM obligations
""")

    obligations_data = cursor.fetchall()

    conn.close()

    return render_template(
        'obligations.html',
        obligations=obligations_data
    )


@app.route('/report')
def report():

    conn = sqlite3.connect('database/contracts.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT obligation_type,
               due_date,
               risk_level,
               summary
        FROM obligations
    """)

    report_data = cursor.fetchall()

    conn.close()

    return render_template(
        'report.html',
        report_data=report_data
    )


@app.route('/reminders')
def reminders():

    conn = sqlite3.connect('database/contracts.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            obligations.obligation_type,
            obligations.due_date,
            obligations.risk_level,
            reminders.reminder_date,
            reminders.status
        FROM reminders
        JOIN obligations
        ON reminders.obligation_id = obligations.id
    """)

    reminders_data = cursor.fetchall()

    conn.close()

    return render_template(
        'reminders.html',
        reminders=reminders_data
    )


if __name__ == '__main__':
    app.run(debug=True)