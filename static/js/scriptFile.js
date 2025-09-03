// scriptFile.js

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageElement = document.getElementById('message');

    const data = {
        username: username,
        password: password
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            messageElement.textContent = 'ログインに成功しました';
            messageElement.style.color = 'green';
            window.location.href = result.redirect_url;
        } else {
            messageElement.textContent = result.error;
            messageElement.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('通信エラー:', error);
        messageElement.textContent = 'エラーが発生しました。';
        messageElement.style.color = 'red';
    });
}

function register() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageElement = document.getElementById('message');

    const data = {
        username: username,
        password: password
    };

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            messageElement.textContent = result.message;
            messageElement.style.color = 'green';
        } else {
            messageElement.textContent = result.error;
            messageElement.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('通信エラー:', error);
        messageElement.textContent = 'エラーが発生しました。';
        messageElement.style.color = 'red';
    });
}

function deleteUser(username) {
    // サーバーへ削除リクエストを送信
    fetch('/delete_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username }),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // 成功したらページをリロードして最新の状態を反映
            alert('ユーザーを削除しました');
            location.reload();
        } else {
            alert('削除に失敗しました: ' + result.error);
        }
    })
    .catch(error => {
        console.error('通信エラー:', error);
        alert('通信エラーが発生しました');
    });
}