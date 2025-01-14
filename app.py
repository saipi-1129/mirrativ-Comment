from flask import Flask, render_template, request
import requests
import datetime
import re

# Webアプリ作成
app = Flask(__name__, static_folder='./templates/images')

# エンドポイント設定（ルーティング）
@app.route('/')
def fetch_online_users():
    # live_idをクエリパラメータまたはPOSTデータから取得
    live_id = request.args.get('live_id', '') or request.form.get('liveid', '')

    if not live_id:
        return render_template("index.html", names=False, comment=False, error="Live ID is required.")
    else:
        # URLが渡される想定で、その中からlive_idを正規表現で抽出
        pattern = r"live/([a-zA-Z0-9_]+)"
        match = re.search(pattern, live_id)  # live_idの中にURLが渡されたと想定して正規表現マッチ
        if match:
            live_id = match.group(1)  # live_idを更新
        else:
            # live_idがURL形式でない場合も、単にlive_idとして使う
            pass
        
        url = f"https://www.mirrativ.com/api/live/live_comments?live_id={live_id}"
        # headers = {
        #     'User-Agent': 'MR_APP/10.45.3/Android/PIXEL 8/12',
        # }
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            comment = data.get('comment', [])
            comment_list = []
            
            comments = data.get('comments', [])
            comment_list = []

            for c in comments:
                name = c.get('user_name', '').encode().decode('utf-8', 'ignore')  
                comment_text = c.get('comment', '')  

                
                comment_list.append({'name': name, 'comment': comment_text})

                print(f'Name: {name}, Comment: {comment_text}')

            names = {item['name']: item['name'] for item in comment_list}
            
            # 現在時刻を取得
            dt_now = datetime.datetime.now()
            print(dt_now.isoformat())
            time = dt_now.isoformat()
            
            return render_template("index.html", time=time, names=names, comment_list=comment_list, error=None)
        else:
            return render_template("index.html", error="Failed to fetch online users. Please try again later.")

# POSTリクエストでlive_idを受け取る
@app.route("/liveid", methods=['POST'])
def liveid():
    live_id = request.form['liveid']
    print(f"[+] LiveId POST Success: {live_id}")
    # POSTされたlive_idを使って再度fetch_online_users関数に処理を行わせる
    return fetch_online_users()

if __name__ == '__main__':  
    app.run(host="0.0.0.0", debug=True)
