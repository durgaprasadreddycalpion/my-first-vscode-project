import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

# 🛠️ DYNAMIC PATH BUILDER:
# Finds the exact folder where app.py sits (the 'backend' folder)
backend_dir = os.path.dirname(os.path.abspath(__file__))

# Point to 'templates' inside the root folder ('my-first-vscode-project')
template_dir = os.path.join(backend_dir, 'templates')


# 🔍 DEBUG PRINTS (Look at your terminal when you start the app!)
print("\n" + "="*50)
print(f"👉 CRITICAL DEBUG INFO:")
print(f"1. Your app.py is running from: {backend_dir}")
print(f"2. Flask is looking for HTML templates in: {template_dir}")
print(f"3. Does that templates folder exist? {'YES' if os.path.exists(template_dir) else '❌ NO, NOT FOUND!'}")
print("="*50 + "\n")

app = Flask(__name__, template_folder=template_dir)
EXCEL_FILE = os.path.join(os.path.dirname(backend_dir), 'database.xlsx')

# Helper function to load data from Excel
def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['ID', 'Name', 'Email'])
        df.to_excel(EXCEL_FILE, index=False)
        return df
    return pd.read_excel(EXCEL_FILE)

# Helper function to save data to Excel
def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

# 1. READ ALL (and homepage)
@app.route('/')
def index():
    df = load_data()
    users = df.to_dict(orient='records')
    return render_template('index.html', users=users)

# 2. CREATE
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    
    df = load_data()
    next_id = int(df['ID'].max() + 1) if not df.empty and pd.notna(df['ID'].max()) else 1
    
    new_row = pd.DataFrame([{'ID': next_id, 'Name': name, 'Email': email}])
    df = pd.concat([df, new_row], ignore_index=True)
    
    save_data(df)
    return redirect(url_for('index'))

# 3. DELETE
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    df = load_data()
    df = df[df['ID'] != user_id]
    save_data(df)
    return redirect(url_for('index'))

# 4. UPDATE (Form Page)
@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    df = load_data()
    
    if request.method == 'POST':
        df.loc[df['ID'] == user_id, 'Name'] = request.form.get('name')
        df.loc[df['ID'] == user_id, 'Email'] = request.form.get('email')
        save_data(df)
        return redirect(url_for('index'))
    
    user_row = df[df['ID'] == user_id]
    if user_row.empty:
        return "User not found", 404
    user = user_row.to_dict(orient='records')[0]
    return render_template('edit.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
