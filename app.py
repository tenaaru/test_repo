from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import secrets
from accountAuth import get_user, check_password, hash_password
from graphGenerator import get_graph_image_path

app = Flask(__name__)
# セッションを使うための秘密鍵を設定
app.secret_key = secrets.token_hex(32)

@app.route('/')
def index():
    # セッションにユーザー名がなければログインページを表示
    if 'username' not in session:
        return render_template('index.html')
    # ユーザー名があれば、ログイン後のページにリダイレクト
    return redirect(url_for('user_home'))

@app.route('/login', methods=['POST'])
def login():
    """認証処理"""
    data = request.get_json()
    # フォームに入力されたユーザ名とパスワードを取得
    username = data.get('username')
    password = data.get('password')

    # アカウント認証関数を呼び出し、ユーザ情報を取得
    user = get_user(username)

    if user:
        # accountAuth.pyのcheck_password関数を使ってパスワードを照合
        if check_password(password, user['password_hash']):
            # 認証成功: セッションにユーザー情報を保存
            session['username'] = user['username']
            session['role'] = user['role']
            print(f"Login successful for user: {user['username']}")

            # ロールに応じて異なるページにリダイレクト
            if user['role'] == 'admin':
                return jsonify({'success': True, 'redirect_url': url_for('admin_page')})
            else:
                return jsonify({'success': True, 'redirect_url': url_for('user_home')})
        else:
            # パスワードが一致しない
            return jsonify({'success': False, 'error': 'Invalid password.'})
    else:
        # ユーザーが見つからない
        return jsonify({'success': False, 'error': 'User not found.'})

@app.route('/user_home')
def user_home():
    # ユーザーがログインしているかチェック
    if 'username' not in session:
        return redirect(url_for('index'))
    graph_data_list = get_graph_image_path()
    return render_template('userWindow.html', name=session['username'],
                           html_graph_data_list=graph_data_list)

@app.route('/admin')
def admin_page():
    # 管理者画面
    if 'role' not in session or session['role'] != 'admin':
        # 認証エラー
        return "Access Denied", 403

    return render_template('adminWindow.html')

@app.route('/logout')
def logout():
    # セッションからユーザー情報を削除
    session.pop('username', None)
    session.pop('role', None)

    return redirect(url_for('index'))

@app.route('/app')
def app_page():
    """アプリ画面"""


    # セッションからユーザー名を取得し渡す
    return render_template('userWindow.html', name=session.get('username'),
                           )

@app.route('/register', methods=['GET'])
def register_page():
    """新規登録画面の表示"""
    return render_template('userRegister.html')

@app.route('/register', methods=['POST'])
def register():
    """新規ユーザー登録処理"""
    # リクエストボディからJSONデータを取得
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # ユーザー名とパスワードが空でないかチェック
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required.'})

    # 既存ユーザーをチェック
    user = get_user(username)
    if user:
        return jsonify({'success': False, 'error': 'User already exists.'})

    try:
        # パスワードをハッシュ化
        hashed_password = hash_password(password).decode('utf-8')
        
        # DynamoDBに新しいユーザーを保存
        from accountAuth import users_table
        users_table.put_item(
            Item={
                'username': username,
                'password_hash': hashed_password,
                'role': 'user'  # デフォルトロール
            }
        )
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed.'})

if __name__ == '__main__':
    # サーバーを起動
    app.run(debug=True)