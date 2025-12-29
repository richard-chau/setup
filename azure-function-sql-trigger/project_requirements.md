# Azure Function Trigger 项目需求文档

## 1. 项目目标
创建一个 Azure Function Trigger 项目，用于执行特定任务（计算/处理）并将结果存储到数据库。项目需要保持轻量级（简洁），但必须具备良好的代码复用性（特别是数据库连接和脚手架代码），以便未来扩展。

## 2. 核心架构决策

### 2.1 运行模型
- **Azure Functions (Serverless)**: 采用原生 Function App 模型。
- **理由**: 自动扩缩容，免去维护 Web Server 的繁琐，适合事件驱动。

### 2.2 存储方案
- **首选**: Azure SQL Database。
  - **理由**: 免费额度高 (Serverless Tier)，适合结构化数据。
- **备选**: Cosmos DB。
  - **理由**: 开发速度快，支持 Output Binding，但成本控制需注意。
- **决策**: 优先实现 SQL Database 的连接与写入逻辑。

### 2.3 代码结构 (简洁 vs 复用)
为了在 "小项目" 和 "复用性" 之间取得平衡，采用 **Shared Module** 模式：
- **`Shared/` 目录**: 存放通用的 `db_client` (数据库连接池管理) 和业务逻辑。
- **Function 目录**: 只包含 `function.json` (配置) 和极简的入口代码 (`__init__.py`)，只负责解析请求和调用 `Shared` 中的逻辑。
- **优势**: 避免了将所有逻辑写在 Trigger 函数内部，也无需打包成复杂的独立 Library。

## 3. 开发与验证环境

### 3.1 本地开发工具
- **Azure Functions Core Tools (`func`)**: 用于本地启动 Function Host。
- **模拟器**: Azurite (如果涉及 Blob/Queue 触发器或 Timer 触发器的状态存储)。

### 4. 最终实现总结

### 4.1 项目结构 (已实现)
```text
azure-function-sql-trigger/
├── host.json                # 全局配置
├── local.settings.json      # 本地连接串 (SqlConnectionString)
├── requirements.txt         # 依赖 (pyodbc, azure-functions)
├── Shared/                  # 复用逻辑层 (核心 "Lib")
│   ├── __init__.py
│   └── db_manager.py        # 数据库连接池与执行助手
└── HttpTriggerTest/         # 示例触发器
    ├── function.json
    └── __init__.py          # 业务入口，调用 Shared 模块
```

### 4.2 核心优化技术
- **连接复用 (Connection Pooling)**: 在 `db_manager.py` 中使用全局变量缓存 SQL 连接。这是 Serverless 环境下的最佳实践，可显著减少“暖启动”时的数据库握手开销。
- **Shared Module 模式**: 既保证了代码复用，又避免了将逻辑分散在多个不相关的 Package 中，保持项目简洁。

### 4.3 本地验证指南 (Docker SQL 方案)
本项目已配置为使用 **Local Docker SQL Server** 进行全栈模拟，无需真实的 Azure 账号。

1.  **启动数据库**:
    ```bash
    # 已自动配置，如需重启：
    docker run --cap-add SYS_PTRACE -e 'ACCEPT_EULA=1' -e 'MSSQL_SA_PASSWORD=Strong!Pass123' -p 1433:1433 --name sql_server -d mcr.microsoft.com/azure-sql-edge
    ```
2.  **初始化表**:
    ```bash
    cd azure-function-sql-trigger
    source .venv/bin/activate
    python3 setup_local_db.py
    ```
3.  **启动 Function**:
    ```bash
    func start
    ```
4.  **测试**:
    -   请求: `curl "http://localhost:7071/api/HttpTriggerTest?name=DockerUser"`
    -   验证: `python3 verify_data.py` (查看数据库写入结果)

### 4.4 最近更新 (2025-12-27)
-   **Local SQL Integration**: 成功集成 Azure SQL Edge (Docker)，并在 `local.settings.json` 中配置了本地连接串。
-   **Bug Fix**: 修复了 SQL 语句中 `User` 关键字未转义导致写入失败的问题。
-   **Verification**:
    -   `verify_sqlite.py`: 验证本地 SQLite 读写。
    -   `verify_blob.py`: 验证 Azurite Blob 存储。
    -   `verify_data.py`: 验证 Docker SQL 数据写入。

## 5. 云端部署 (Completed 2025-12-27)

项目已成功部署至 Azure Cloud，并实现了端到端联调。

### 5.1 云资源清单
-   **Resource Group**: `beginner`
-   **Region**: `westus2`
-   **Function App**: `sql-trigger-64568d` (Python 3.11, Consumption Plan)
    -   URL: `https://sql-trigger-64568d.azurewebsites.net/api/httptriggertest`
-   **SQL Server**: `alexbeginner.database.windows.net`
-   **Database**: `alexbeginner` (Serverless Tier)
-   **Storage Account**: `beginnerbf9b`

### 5.2 部署过程回顾
1.  **环境准备**: 安装 Azure CLI (`az`) 并完成登录。
2.  **数据库配置**:
    -   重置 SQL Admin 密码。
    -   配置防火墙规则 `AllowAzureServices` (允许 Function 访问) 和 `DevBox` (允许本地 IP 141.148.150.146 管理)。
3.  **资源创建**:
    -   使用 `deploy_cloud.sh` 脚本自动创建了 Function App。
    -   配置了 App Settings (`SqlConnectionString`)。
4.  **代码发布**: 使用 `func azure functionapp publish` 上传代码。
5.  **Schema 初始化**:
    -   运行 `setup_cloud_db.py` 远程连接云数据库。
    -   创建了 `AccessLogs` 表。
6.  **验证**:
    -   `curl` 请求成功返回 "Hello, FinalCloudSuccess. (DB interaction successful)"。
    -   确认数据库已写入记录。

### 5.3 常用运维命令
-   **获取 Function Key**:
    ```bash
    az functionapp function keys list --resource-group beginner --name sql-trigger-64568d --function-name HttpTriggerTest --query "default" -o tsv
    ```
-   **查看实时日志**:
        ```bash
        func azure functionapp logstream sql-trigger-64568d
        ```
    
    ## 6. Developer Guide: Fast-Track Process
    
    **核心成果**: 本项目已建立了一套可复用的“Azure Function 工厂”。未来开发新功能的时间可缩短至 15 分钟以内。
    
    ### 6.1 复用资产 (不要重复造轮子)
    -   **基础设施**: 本地 Docker (SQL & Azurite) 可长期运行，供所有项目共享。
    -   **核心代码**: `Shared/db_manager.py` 封装了连接池和重试逻辑，**直接复制**到新项目即可。
    -   **部署脚本**: `deploy_cloud.sh` 只需修改 `FUNCTION_APP_NAME` 即可用于部署新应用。
    
    ### 6.2 新功能开发流程 (15分钟)
    
    **Step A: 本地开发 (10分钟)**
    1.  **创建**: `func new --name MyNewCalc --template "HTTP trigger"`
    2.  **连接**: 在代码中 `import Shared.db_manager`。
    3.  **运行**: `func start` (自动连接本地 Docker SQL)。
    
    **Step B: 云端部署 (5分钟)**
    1.  **建表**: 参考 `setup_cloud_db.py` 在云端创建业务表。
    2.  **部署**:
        -   *复用 App*: `func azure functionapp publish sql-trigger-64568d`
        -   *新 App*: 修改 `deploy_cloud.sh` 并运行。
    
    ### 6.3 本地环境管理
    新增脚本 `manage_local_env.sh` 用于快速控制本地服务：
    ```bash
    chmod +x manage_local_env.sh
    ./manage_local_env.sh start   # 启动 SQL/Azurite
    ./manage_local_env.sh stop    # 暂停服务 (释放内存)
    ./manage_local_env.sh clean   # 删除容器和数据 (重置环境)
    ```
    