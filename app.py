from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import secrets
import yfinance as yf
from datetime import date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

app = Flask(__name__)

# ユーザー情報
# 初期要件では辞書型で定義する。追加機能でデータベースに移行する。
USERS = {
    "root": {"password": "root", "role": "admin"},
    "sota": {"password": "sota", "role": "user"}
}

# 銘柄情報()と会社名
# 今後でデータベースに移行するかも
TICKERS = {
    "AAPL": "Apple Inc.",
    "7203.T": "TOYOTA MOTOR CORPORATION",
    "NVDA": "NVIDIA Corporation",
    "7974.T": "Nintendo Co., Ltd."
}

# セッションを使うための秘密鍵を設定
app.secret_key = secrets.token_hex(32)

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
    # 現在の年月日を取得。終了日としても利用する
    today = date.today()
    # 開始日を設定。10週間前とする。
    startDay = today - timedelta(weeks=10)

    # グラフ画像のファイルパスと会社名を格納するリスト
    dataList = []

    for tickerSymbol, companyName in TICKERS.items():
        try:
            data = yf.download(
                tickers=tickerSymbol,
                start=startDay,
                end=today,
                interval='1wk'
            )
            if data.empty:
                # 株価情報の取得に失敗
                print(f"No data found for {companyName}")
                dataList = ({
                    'path': url_for('static', filename='images/graphError.png'),
                    'name': companyName
                })
                continue
            # グラフ描画後、画像ファイルとして保存
            plt.figure(figsize=(10, 6))
            plt.plot(mdates.date2num(data.index), data['Open'], marker='.')
            plt.title(f'{companyName} (10 weaks)')
            plt.xlabel('Date')
            plt.ylabel('Stock Price')
            plt.grid(True)
            plt.gca().set_xticks(data.index)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))
            plt.tight_layout()
            # 画像ファイルとして保存
            imgfilename = f'graph_{tickerSymbol}.png'
            imgpath = os.path.join('static', 'images', imgfilename)
            plt.savefig(imgpath)
            plt.close()
            
            dataList.append({
                'path': url_for('static', filename=f'images/{imgfilename}'),
                'name': companyName
            })

        except Exception as e:
            print(f"Error processing ticker {tickerSymbol}: {e}")
            continue
    # セッションからユーザー名を取得し渡す
    return render_template('userWindow.html', name=session.get('username'),
                           html_dataList=dataList)

if __name__ == '__main__':
    # サーバーを起動
    app.run(debug=True)