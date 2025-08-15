from flask import Flask, request, jsonify, render_template, session, redirect, url_for


app = Flask(__name__)

# ユーザー情報（実際はデータベースから取得）
# シンプルなデモのため、辞書型で定義
USERS = {
    "root": {"password": "root", "role": "admin"},
    "sota": {"password": "sota", "role": "user"}
}

# セッションを使うための秘密鍵を設定
app.secret_key = 'secret_key'

@app.route('/')
def home():
    """トップページ（ログイン画面）を表示"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """認証処理"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = USERS.get(username)

    if user and user['password'] == password:
        # 認証成功
        session['username'] = username
        return jsonify(success=True, role=user['role'])
    else:
        # 認証失敗
        return jsonify(success=False)

@app.route('/admin')
def admin_page():
    """管理者画面"""
    return render_template('adminWindow.html')

@app.route('/app')
def app_page():
    """アプリ画面"""
    # セッションからユーザー名を取得
    username = session.get('username')
    return render_template('userWindow.html', name=username)

if __name__ == '__main__':
    # サーバーを起動
    app.run(debug=True)