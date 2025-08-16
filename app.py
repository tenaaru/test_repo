from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import secrets
import yfinance as yf

app = Flask(__name__)

# ユーザー情報
# 初期要件では辞書型で定義する。追加機能でデータベースに移行する。
USERS = {
    "root": {"password": "root", "role": "admin"},
    "sota": {"password": "sota", "role": "user"}
}

# セッションを使うための秘密鍵を設定
secretKey = secrets.token_hex(32)
app.secret_key = secretKey

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
    # 任天堂の5週間分の株価を1週間間隔で取得
    apple = yf.Ticker("NTDOY")
    data1 = apple.history(period="5wk", interval="1wk")
    # セッションからユーザー名を取得し渡す
    return render_template('userWindow.html', name=session.get('username'), tickerData1=data1)

if __name__ == '__main__':
    # サーバーを起動
    app.run(debug=True)