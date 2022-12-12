from src.revChatGPT import revChatGPT
from src.revChatGPT.__main__ import CaptchaSolver
import json
from os.path import exists
import traceback

users = {}
config_files = ["config.json"]
config_file = next((f for f in config_files if exists(f)), None)
if not config_file:
    print("Please create and populate ./config.json, $XDG_CONFIG_HOME/revChatGPT/config.json, or ~/.config/revChatGPT/config.json to continue")
    exit()

with open(config_file, encoding="utf-8") as f:
    config = json.load(f)
robot = revChatGPT.Chatbot(config,debug=True,
                           captcha_solver=CaptchaSolver())


from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder="templates",
            static_folder="templates",
            static_url_path="")
@app.route('/chat')
def chat():
    global users
    text = request.args.get('text')
    user = request.args.get('user')
    conversation_id = None
    parent_id = None
    conversation_id = request.args.get('conversation_id')
    parent_id = request.args.get('parent_id')
    print('请求消息',user,conversation_id,parent_id,text)
    _robot = None
    if user in users:
        _robot = users[user]
        if _robot.conversation_id != conversation_id:
            print('[对话已重置]')
            _robot = None
  
    if _robot == None:
        if conversation_id != None and parent_id != None:
            print('[对话恢复]',conversation_id,parent_id)
        else:
            print('[新用户]',user)
        _robot = revChatGPT.Chatbot(config,debug=True,captcha_solver=CaptchaSolver(),conversation_id = conversation_id,parent_id = parent_id)
        users[user] = _robot


    try:
        if text == "!重启":
            _robot.refresh_session()
            msg = {"message":"重启完毕"}
        elif text == "!回滚":
            _robot.rollback_conversation()
            msg = {"message":"回滚完毕"}
        elif text == "!洗脑":
            _robot.reset_chat()
            msg = {"message":"好的让我重新开始对话吧"}
        elif text == "!AI重置":
            msg = {"message":"重置完毕"}
            users = {}
        else:
            msg = _robot.get_chat_response(text)
    except Exception as e:
        _robot.reset_chat()
        exc = traceback.format_exc()
        _robot.refresh_session()
        print("ERROR",exc)
        msg = {"message":"警告！警告！已过载！，3秒后重启..."}
    print('用户',user,'ID:',_robot.conversation_id)

    print(msg)
    return msg

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host="0.0.0.0", port=8889)


