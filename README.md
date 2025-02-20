# fnWifi

fnWifi 是一个基于GitHub Copilot的AI Code能力，为飞牛OS开发的简单的应用程序，用于列出可用的 WiFi 网络，并允许用户连接或断开 WiFi 网络。

## 功能

- 列出可用的 WiFi 网络
- 显示 WiFi 网络的 SSID、安全性和信号强度
- 连接到 WiFi 网络
- 断开 WiFi 网络
- 
![界面预览](https://tu.tryto.live:808/i/2025/02/20/193607.png)


## 安装

1. 克隆此仓库到本地：
    ```bash
    git clone https://github.com/EDYSuperCore/fnWifi.git
    ```

2. 进入项目目录：
    ```bash
    cd fnWifi
    ```

3. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

4. 确保您具有 `sudo` 权限，并以 `sudo` 权限运行以下命令启动服务器：
    ```bash
    sudo python main.py
    ```

## 使用

1. 启动服务器后，打开浏览器并访问 `http://localhost:8100`。
2. 页面将显示可用的 WiFi 网络列表。
3. 点击“连接”按钮，输入 WiFi 密码并点击“连接”以连接到 WiFi 网络。
4. 点击“断开”按钮以断开当前连接的 WiFi 网络。

## 文件结构

- `main.py`：主服务器脚本，处理 WiFi 列表、连接和断开请求。
- `web/`：前端文件夹，包含 HTML、CSS 和 JavaScript 文件。
  - `index.html`：主页面文件。
  - `styles.css`：样式文件。
  - `scripts.js`：JavaScript 文件，处理前端逻辑。
- `requirements.txt`：Python 依赖文件。


## 许可证

MIT License

版权所有 (c) 2023 MJ

特此免费授予任何获得本软件和相关文档文件（“软件”）副本的人无限制地处理本软件，包括但不限于使用、复制、修改、合并、出版、分发、再许可和/或出售本软件的副本的权利，并允许本软件提供给其的人员这样做，但须符合以下条件：

上述版权声明和本许可声明应包含在本软件的所有副本或主要部分中。

本软件按“原样”提供，不作任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性和非侵权性的担保。在任何情况下，作者或版权持有人均不对因本软件或本软件的使用或其他交易而产生的任何索赔、损害或其他责任负责，无论是在合同诉讼、侵权诉讼或其他诉讼中。

## 生成说明

此项目的代码完全基于 GitHub Copilot 的 AI 能力生成。