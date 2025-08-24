from flask import url_for
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import date, timedelta

# DynamoDBに接続するための設定
dynamodb = boto3.resource('dynamodb')
# DynamoDBのグラフ画像情報のテーブル名
graph_img_table = dynamodb.Table('KABU_graphImgInfoTable')

# 銘柄リストを定義
TICKERS = {
    "AAPL": "Apple Inc.",
    "7203.T": "TOYOTA MOTOR CORPORATION",
    "NVDA": "NVIDIA Corporation",
    "7974.T": "Nintendo Co., Ltd."
}

def get_graph_image_path():
    # 現在の年月日を取得。終了日としても利用する
    today_str = date.today().strftime('%Y-%m-%d')

    # グラフ画像のファイルパスを格納するリスト
    graph_data_list = []
    for stock_code in TICKERS.keys():
        try:
            # DynamoDBのQueryを使って、パーティションキーとタイムスタンプでアイテムを検索
            response = graph_img_table.query(
                KeyConditionExpression=Key('stockcode').eq(stock_code),
                FilterExpression=Attr('timestamp').begins_with(today_str)
            )

            # 一致するレコードが見つかった場合
            if response.get('Items'):
                item = response['Items'][0]
                image_path = item.get('imagepath')
                
                # ファイルパスに実際に画像ファイルが存在するか確認
                if os.path.exists(image_path):
                    # 存在するならリストに追加
                    graph_data_list.append({
                        'company_name': item.get('companyname'),
                        'image_path': image_path
                    })
                else:
                    # ファイルが存在しない場合、新しいグラフを生成し、DynamoDBを更新
                    today_date_obj = date.today()
                    start_date_obj = today_date_obj - timedelta(weeks=10)
                    image_filepath = generate_stock_graph(stock_code, start_date_obj, today_date_obj)

                    # DynamoDBのレコードを更新
                    graph_img_table.put_item(
                        Item={
                            'stockcode': stock_code,
                            'companyname': item.get('companyname'),
                            'timestamp': today_str,
                            'imagepath': image_filepath
                        }
                    )
                    
                    # 新しい画像パスと会社名をリストに追加
                    graph_data_list.append({
                        'company_name': item.get('companyname'),
                        'image_path': image_filepath
                    })
            else:
                # 一致するレコードが見つからなかった場合、新しいグラフを生成し保存
                today = date.today()
                # 開始日を設定。10週間前とする。
                start_day = today - timedelta(weeks=10)
                # generate_stock_graph関数を呼び出し、新しい画像パスを取得
                image_filepath = generate_stock_graph(stock_code, start_day, today)
                
                # 会社名を取得
                company_name = TICKERS.get(stock_code)

                graph_img_table.put_item(
                    Item={
                        'stockcode': stock_code,
                        'companyname': TICKERS.get(stock_code),
                        'timestamp': today_str,
                        'imagepath': image_filepath
                    }
                )
                # 新しい画像パスと会社名をリストに追加
                graph_data_list.append({
                    'company_name': company_name,
                    'image_path': image_filepath
                })

        except Exception as e:
            print(f"Error querying DynamoDB for {stock_code}: {e}")
            # エラー発生時の代替画像と会社名を追加
            graph_data_list.append({
                'company_name': "Unknown",
                'image_path': url_for('static', filename='images/graphError.png')
            })
            continue
    return graph_data_list

def generate_stock_graph(ticker_symbol, start_date, end_date):
    """
    株価データを取得し、グラフを生成してファイルに保存する関数
    :param ticker_symbol: 銘柄コード (例: 'AAPL')
    :param start_date: データの取得開始日 (datetime.dateオブジェクト)
    :param end_date: データの取得終了日 (datetime.dateオブジェクト)
    :return: 成功した場合は画像のファイルパス、失敗した場合はNoneを返す
    """
    try:
        data = yf.download(
            tickers=ticker_symbol,
            start=start_date,
            end=end_date,
            interval='1wk'
        )
        if data.empty:
            # 株価情報の取得に失敗
            print(f"No data found for {ticker_symbol}")
            return None

        plt.figure(figsize=(10, 6))
        plt.plot(mdates.date2num(data.index), data['Close'], marker='.')
        plt.title(f'Stock Price (10 Weeks)')
        plt.xlabel('Date')
        plt.ylabel('Stock Price')
        plt.grid(True)
        plt.gca().set_xticks(data.index)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))
        plt.tight_layout()

        # 画像ファイルの保存先パスを生成
        imgfilename = f'graph_{ticker_symbol}.png'
        # ディレクトリが存在するか確認し、なければ作成
        img_dir = os.path.join('static', 'images')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        
        imgpath = os.path.join('static', 'images', imgfilename)
        
        plt.savefig(imgpath)
        plt.close()

        return imgpath

    except Exception as e:
        print(f"Error generating graph for {ticker_symbol}: {e}")
        return None