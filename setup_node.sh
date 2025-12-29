#!/bin/bash

echo "正在更新系统并安装 Node.js 20..."
# 1. 导入 NodeSource 官方仓库 (Node 20)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 2. 安装 Node.js 和构建工具
sudo apt-get install -y nodejs build-essential

# 3. 配置 npm 全局目录到家目录 (解决之前的 Permission Denied 报错)
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
if ! grep -q "npm-global" ~/.profile; then
    echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.profile
fi
source ~/.profile

# 4. 安装 pm2 (进程守护工具，防止 n8n 崩溃)
npm install -g pm2

echo "---------------------------------------"
echo "安装完成！当前版本信息："
node -v
npm -v
pm2 -v
echo "---------------------------------------"
echo "提示：如果 gemini 命令还提示找不到，请运行一次: source ~/.profile"
