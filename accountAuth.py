import boto3
import bcrypt
from botocore.exceptions import ClientError

# DynamoDBに接続するための設定
dynamodb = boto3.resource('dynamodb')
# DynamoDBのアカウント情報のテーブル名
users_table = dynamodb.Table('KABU_AccountTable')

def hash_password(password):
    """
    パスワードをハッシュ化する関数
    :param password: ハッシュ化前の平文パスワード
    :return: ハッシュ化されたバイト文字列
    """
    password_bytes = password.encode('utf-8')
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt())

def check_password(password, hashed_password):
    """
    平文パスワードとハッシュ化されたパスワードを比較する関数
    :param password: ユーザーが入力した平文パスワード
    :param hashed_password: DynamoDBに保存されているハッシュ化されたパスワード
    :return: パスワードが一致すればTrue、そうでなければFalse
    """
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def get_user(username):
    """
    DynamoDBからユーザー情報を取得する関数
    :param username: 取得したいユーザー名
    :return: ユーザー情報（辞書）またはNone
    """
    try:
        response = users_table.get_item(Key={'username': username})
        return response.get('Item')
    except ClientError as e:
        print(f"DynamoDB get_item error: {e.response['Error']['Message']}")
        return None