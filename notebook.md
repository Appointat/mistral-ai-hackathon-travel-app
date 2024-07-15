### 如何启动？

1. Open WebUI（前端）
   1. git clone https://github.com/Appointat/open-webui
   2. 参考官方的说明书，来启动这个项目（https://docs.openwebui.com/getting-started/#install-from-open-webui-github-repo）
2. travel-app（临时一个repo，后面再改名）（后端）
   1. git clone https://github.com/Appointat/mistral-ai-hackathon-travel-app
   2. 激活虚拟环境
   3. 安装pip install -r requirements.txt
   4. 在terminal添加环境变量（每次启动新的terminal都要做这一步）：$env:OPENAI_API_KEY="sk-****"(windows)
   5. python set_up.py （里面主要执行的是role_playing_async.py函数，这个是非multi agents的版本，做demo足够了）
       - 强制使用gpt4-o模型
3. 开始聊天
   1. 打开 http://localhost:8080
   2. 随便选择一个model，非空即可
   3. 输入你的消息，等待异步的回复即可。
      1. 聊天记录不支持连续对话。
      2. 输出的语言会是中文（强制性的）。
   4. 建议你的第一条prompt：Compose a very challenging system design problem for deep learning, and then solve this difficult issue step by step.
4. 查看可视化脑图
   1. 每次对话之后会生成一张脑图，用浏览器打开：apps\streamlit_ui\cache\mind_map.html
