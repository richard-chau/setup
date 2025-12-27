#!/bin/bash

# 设置 Swap 文件大小为 2G
SWAP_SIZE="2G"
SWAP_PATH="/swapfile"

echo "开始创建 ${SWAP_SIZE} 的 Swap 空间..."

# 1. 创建空文件
sudo fallocate -l $SWAP_SIZE $SWAP_PATH || sudo dd if=/dev/zero of=$SWAP_PATH bs=1M count=2048

# 2. 设置权限 (仅 root 可读写)
sudo chmod 600 $SWAP_PATH

# 3. 格式化为 Swap
sudo mkswap $SWAP_PATH

# 4. 启用 Swap
sudo swapon $SWAP_PATH

# 5. 设置开机自启 (防止重复添加)
if ! grep -q "$SWAP_PATH" /etc/fstab; then
    echo "$SWAP_PATH none swap sw 0 0" | sudo tee -a /etc/fstab
    echo "已添加开机自启配置。"
fi

# 6. 优化性能参数 (Swappiness)
sudo sysctl vm.swappiness=10
if ! grep -q "vm.swappiness=10" /etc/sysctl.conf; then
    echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
    echo "已优化 Swappiness 参数。"
fi

echo "Swap 设置完成！当前内存状态："
free -h
