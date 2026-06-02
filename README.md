简易社交平台（Flask + MySQL）

对应实验要求：
- 用户注册、登录与个人信息修改
- 好友搜索、添加、删除与分组管理
- 朋友圈发布、编辑、删除（含字数限制与最后更新时间）
- 查看好友动态与评论互动
- 删除动态时自动删除评论（外键级联）
- 管理员登录、修改信息、审核/删除动态、注销用户
- 触发器与事务：
	- 触发器更新动态最后更新时间
	- 管理员注销用户使用事务处理

快速开始：
1. 编辑 config.py（或复制 config.py.example）填写 MySQL 连接。
2. 安装依赖：pip install -r requirements.txt
3. 运行：python app.py

首次启动会自动建表并创建示例账号：
- 管理员：admin / password
- 用户：user / password、alice / password

项目结构：
- app.py：应用入口与启动
- app/db.py：数据库连接、初始化与种子数据
- app/repositories/：数据访问层
- app/services/：业务逻辑层
- app/routes/：路由层
- app/templates/：页面模板
- app/static/：样式与静态资源
- schema.sql：数据库表、触发器与视图

前端说明：
- 页面使用统一布局与 CSS 主题
- 朋友圈与好友管理界面已补充交互与分组分配入口