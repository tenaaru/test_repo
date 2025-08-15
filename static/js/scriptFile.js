function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageElement = document.getElementById('message');

    // サーバーに送信するデータ
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
            // 認証成功
            alert('ログインに成功しました');
            // messageElement.textContent = 'ログイン成功！';
            if (result.role === 'admin') {
                window.location.href = '/admin'; // 管理者画面へ
            } else {
                window.location.href = '/app'; // アプリ画面へ
            }
        } else {
            // 認証失敗 
            alert('ログインに失敗しました');
            // messageElement.textContent = 'ログインに失敗しました。';
        }
    })
    .catch(error => {
        console.error('通信エラー:', error);
        messageElement.textContent = 'エラーが発生しました。';
    });
}