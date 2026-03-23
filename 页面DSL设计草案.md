# 页面 DSL 设计草案

## 1. 文档目标

本文档用于定义“数据应用 Vibe Coding 平台”的页面 DSL 初步设计方案。该 DSL 不是通用网页描述协议，而是专门面向以下场景：

- 基于数据仓库的数据应用
- BI 大屏
- 数据查询页
- 指标分析页
- Data Agent 展示页
- Data Agent 执行页

页面 DSL 的目标不是替代 React 或前端源码，而是作为平台的中间表示层，用于承接：

- 自然语言生成
- 可视化编辑
- 版本管理
- 应用发布
- 源码导出

## 2. 为什么需要页面 DSL

如果平台直接让大模型输出 React、SQL、样式和交互源码，会产生几个问题：

- 生成结果不稳定
- 后续难以结构化修改
- 可视化编辑难落地
- 数据绑定和权限规则难治理
- 版本 diff、回滚和发布管理复杂

因此更合理的方式是：

1. 用户通过自然语言描述需求
2. 平台将需求转成页面 DSL
3. 页面运行时根据 DSL 渲染出实际页面
4. 用户继续通过对话或可视化方式修改 DSL
5. 发布系统根据 DSL 进行预览、版本化和上线

页面 DSL 的角色是：

- 页面定义协议
- 组件组织协议
- 数据绑定协议
- 交互逻辑协议
- 权限与发布协议

## 3. DSL 设计原则

### 3.1 可读性优先

DSL 应尽量具备较强可读性，使得：

- 模型容易生成
- 平台容易解析
- 人类也能调试

### 3.2 声明式优先

DSL 应尽量采用声明式表达，而不是命令式流程编排。

例如：

- 描述“这个图表展示什么”
- 而不是描述“页面加载后按步骤执行哪些 DOM 操作”

### 3.3 面向数据应用

DSL 需要天然支持：

- 指标
- 维度
- 查询
- 筛选器
- 图表
- 表格
- Agent 面板

而不是先做一个通用组件协议，再勉强适配数据应用。

### 3.4 可版本化

DSL 必须天然支持版本管理，便于：

- diff
- 回滚
- 审批
- 灰度发布

### 3.5 可导出

DSL 不等于平台运行时绑定死。它未来应支持导出为：

- React/Next.js 源码
- JSON 配置
- 嵌入式运行包

## 4. DSL 在整体架构中的位置

建议平台的整体生成链路如下：

1. 用户输入自然语言需求
2. 模型进行意图解析
3. 语义层提供业务上下文
4. 生成引擎输出页面 DSL
5. 页面运行时根据 DSL 渲染页面
6. 查询网关负责数据获取
7. Agent 运行时负责问答和执行
8. 发布系统将 DSL 版本上线

在这个链路中：

- 自然语言是输入层
- DSL 是中间层
- 页面运行时是执行层

## 5. DSL 作用范围

第一版 DSL 建议覆盖以下能力：

- 页面级元数据
- 页面布局
- 组件定义
- 数据绑定
- 查询定义
- 交互事件
- 权限要求
- 发布信息

第一版不建议直接把下面这些都塞进 DSL：

- 复杂脚本逻辑
- 任意自定义代码块
- 高自由度视觉动画编排
- 复杂多页面流程引擎

## 6. DSL 顶层结构

建议 DSL 顶层采用如下结构：

```json
{
  "dsl_version": "0.1.0",
  "app": {},
  "page": {},
  "layout": [],
  "widgets": [],
  "queries": [],
  "interactions": [],
  "permissions": {},
  "publish": {}
}
```

含义如下：

- `dsl_version`: DSL 版本号
- `app`: 应用级信息
- `page`: 页面级信息
- `layout`: 布局树
- `widgets`: 组件定义
- `queries`: 查询定义
- `interactions`: 交互逻辑
- `permissions`: 权限与访问控制
- `publish`: 发布信息

## 7. 顶层对象说明

### 7.1 app

用于描述应用级上下文。

建议字段：

- `app_id`
- `app_name`
- `app_type`
- `owner`
- `environment`
- `semantic_model_id`
- `data_source_id`

示例：

```json
{
  "app_id": "sales-dashboard-app",
  "app_name": "销售经营分析",
  "app_type": "dashboard",
  "owner": "team-growth",
  "environment": "production",
  "semantic_model_id": "sales_semantic_v2",
  "data_source_id": "warehouse_prod"
}
```

### 7.2 page

用于描述页面元信息。

建议字段：

- `page_id`
- `title`
- `description`
- `route`
- `page_type`
- `device_mode`
- `theme`

其中：

- `page_type` 可取值：`dashboard`、`analysis`、`query`、`agent_chat`、`agent_action`
- `device_mode` 可取值：`desktop`、`mobile`、`responsive`

### 7.3 layout

用于描述页面布局结构。

建议采用树形容器模型。

基础节点类型：

- `row`
- `column`
- `grid`
- `tabs`
- `section`
- `panel`

每个布局节点建议具备：

- `id`
- `type`
- `children`
- `style`
- `responsive`

## 8. Widget 模型设计

### 8.1 为什么 Widget 是核心

对于数据应用平台，Widget 是页面 DSL 的核心。因为用户最终看到的是：

- KPI
- 图表
- 表格
- 筛选器
- 文本说明
- Agent 面板

所以 Widget 需要统一建模。

### 8.2 Widget 通用字段

建议每个 Widget 具备以下字段：

- `id`
- `type`
- `title`
- `layout_ref`
- `style`
- `data_binding`
- `visibility`
- `permission_ref`
- `events`

### 8.3 Widget 类型建议

第一版建议支持：

- `kpi_card`
- `line_chart`
- `bar_chart`
- `stacked_bar_chart`
- `pie_chart`
- `funnel_chart`
- `table`
- `text_block`
- `filter_bar`
- `date_filter`
- `metric_selector`
- `dimension_selector`
- `agent_chat_panel`
- `agent_result_panel`
- `agent_action_panel`

### 8.4 图表 Widget 特殊字段

图表类 Widget 建议具备：

- `chart_type`
- `x_field`
- `y_fields`
- `group_by`
- `sort`
- `limit`
- `empty_state`
- `legend`

## 9. Query 模型设计

### 9.1 为什么 Query 需要独立定义

不建议把查询逻辑直接塞进每个 Widget 中。

更合理的做法是：

- Widget 引用 Query
- Query 独立定义
- 多个 Widget 可以复用同一个 Query

这样更适合：

- 查询缓存
- 查询治理
- 查询调试
- 权限注入

### 9.2 Query 结构建议

```json
{
  "id": "q_sales_overview",
  "source": "semantic_model",
  "dataset": "sales_daily",
  "metrics": ["gmv", "order_count", "conversion_rate"],
  "dimensions": ["order_date", "channel"],
  "filters": [],
  "time_grain": "day",
  "limit": 1000
}
```

建议字段：

- `id`
- `source`
- `dataset`
- `metrics`
- `dimensions`
- `filters`
- `time_grain`
- `sort`
- `limit`
- `cache_policy`

### 9.3 Query 数据源类型

建议至少支持：

- `semantic_model`
- `metric_model`
- `sql_template`
- `agent_generated_query`

第一版应优先使用：

- `semantic_model`

只有在必要时才暴露：

- `sql_template`

## 10. Interaction 模型设计

### 10.1 为什么要单独描述交互

页面中的交互包括：

- 筛选器联动
- 图表点击钻取
- 表格行点击跳转
- Agent 执行动作确认

这些逻辑如果完全写死在前端代码里，会降低平台可编辑性。

因此建议用独立的 `interactions` 数组描述交互。

### 10.2 交互结构建议

```json
{
  "id": "interaction_date_filter",
  "trigger": {
    "widget_id": "filter_date",
    "event": "change"
  },
  "action": {
    "type": "refresh_query",
    "targets": ["q_sales_overview", "q_sales_trend"]
  }
}
```

常见动作类型：

- `refresh_query`
- `navigate`
- `open_drawer`
- `open_modal`
- `update_widget_state`
- `invoke_agent_action`

## 11. Permission 模型设计

### 11.1 权限为什么要进 DSL

这个平台不是静态 BI，而是涉及：

- 数据展示
- 指标查看
- Agent 执行动作
- 不同角色访问同一页面

因此权限不能只在系统后台控制，页面 DSL 里也要体现“这个页面和组件需要什么权限”。

### 11.2 权限结构建议

建议分为三层：

- 页面权限
- 组件权限
- 动作权限

示例：

```json
{
  "page_access": ["analyst", "manager"],
  "widget_rules": [
    {
      "widget_id": "profit_chart",
      "roles": ["manager"]
    }
  ],
  "action_rules": [
    {
      "action_id": "generate_report",
      "roles": ["analyst", "manager"],
      "approval_required": false
    },
    {
      "action_id": "create_followup_task",
      "roles": ["manager"],
      "approval_required": true
    }
  ]
}
```

## 12. Agent 页面 DSL 设计

### 12.1 Agent 页面和 BI 页面有什么不同

BI 页面重点是展示数据。

Agent 页面除了展示，还涉及：

- 对话输入
- 推荐问题
- 查询结果解释
- 可执行动作
- 权限确认
- 审批状态反馈

因此 Agent 页面 DSL 需要额外支持：

- `agent_config`
- `tool_refs`
- `action_refs`
- `conversation_memory`

### 12.2 Agent 页面顶层扩展字段

建议在 `page` 或 `app` 下增加：

- `agent_id`
- `agent_mode`
- `agent_policy`

其中：

- `agent_mode` 可取值：`query_only`、`query_and_action`

### 12.3 Agent Action Widget 示例

```json
{
  "id": "w_create_task",
  "type": "agent_action_panel",
  "title": "创建跟进任务",
  "layout_ref": "panel_actions",
  "action_ref": "create_followup_task",
  "permission_ref": "manager_only"
}
```

## 13. 响应式与多端设计

### 13.1 是否要把响应式信息写进 DSL

建议要。

原因：

- 同一页面可能同时运行在桌面端和移动端
- 大屏布局和移动布局差异大
- 如果不把响应式规则写进 DSL，平台很难做自动适配

### 13.2 推荐方式

每个布局节点和 Widget 可具备：

- `desktop`
- `tablet`
- `mobile`

三个断点配置。

例如：

- 占几列
- 是否隐藏
- 排序顺序
- 高度和宽度

## 14. DSL 示例：销售经营大屏

以下是一个简化示例：

```json
{
  "dsl_version": "0.1.0",
  "app": {
    "app_id": "sales_dashboard",
    "app_name": "销售经营分析",
    "app_type": "dashboard",
    "semantic_model_id": "sales_semantic_v2",
    "data_source_id": "warehouse_prod"
  },
  "page": {
    "page_id": "sales_overview",
    "title": "销售经营总览",
    "route": "/sales/overview",
    "page_type": "dashboard",
    "device_mode": "responsive"
  },
  "layout": [
    {
      "id": "section_top",
      "type": "grid",
      "children": ["w_gmv", "w_orders", "w_conversion", "w_filter_date"]
    },
    {
      "id": "section_main",
      "type": "grid",
      "children": ["w_trend", "w_channel_table"]
    }
  ],
  "widgets": [
    {
      "id": "w_gmv",
      "type": "kpi_card",
      "title": "GMV",
      "layout_ref": "section_top",
      "data_binding": {
        "query_id": "q_sales_overview",
        "metric": "gmv"
      }
    },
    {
      "id": "w_trend",
      "type": "line_chart",
      "title": "销售趋势",
      "layout_ref": "section_main",
      "data_binding": {
        "query_id": "q_sales_trend"
      }
    }
  ],
  "queries": [
    {
      "id": "q_sales_overview",
      "source": "semantic_model",
      "dataset": "sales_daily",
      "metrics": ["gmv", "order_count", "conversion_rate"]
    },
    {
      "id": "q_sales_trend",
      "source": "semantic_model",
      "dataset": "sales_daily",
      "metrics": ["gmv"],
      "dimensions": ["order_date"],
      "time_grain": "day"
    }
  ],
  "interactions": [
    {
      "id": "date_filter_change",
      "trigger": {
        "widget_id": "w_filter_date",
        "event": "change"
      },
      "action": {
        "type": "refresh_query",
        "targets": ["q_sales_overview", "q_sales_trend"]
      }
    }
  ]
}
```

## 15. 生成与编辑流程

建议 DSL 的编辑分三类：

### 15.1 自然语言生成

模型根据需求直接生成 DSL 草稿。

### 15.2 可视化编辑

用户拖拽、增删组件、修改绑定，平台更新 DSL。

### 15.3 对话式修改

用户说：

- “增加利润率趋势图”
- “把表格移动到下方”
- “这个页面改成更适合移动端”

平台解析后修改 DSL，再刷新预览。

## 16. DSL 与源码导出的关系

页面 DSL 不是源码本身，但应支持导出源码。

建议导出链路为：

1. DSL
2. Code Generator
3. React/Next.js 页面源码
4. 补充测试与配置文件

其中：

- 平台日常运行依赖 DSL runtime
- 导出源码时再调用代码生成器

## 17. 第一版不建议支持的能力

为了控制复杂度，第一版 DSL 不建议支持：

- 任意 JavaScript 脚本注入
- 任意 SQL 在线编辑暴露给终端用户
- 复杂多页面事务流程
- 复杂动画编排
- 完整表单系统

## 18. 后续迭代方向

后续可扩展方向包括：

- 多页面路由 DSL
- 表单与写操作 DSL
- Agent 工具注册 DSL
- 应用级主题系统
- 页面嵌入协议
- 团队级组件模板

## 19. 结论

页面 DSL 是该平台的关键中间层。它让自然语言生成、可视化编辑、运行时渲染、权限治理和源码导出变成同一套结构化体系。

对于这个“面向数据仓库的数据应用 Vibe Coding 平台”来说，页面 DSL 不是可有可无的实现细节，而是产品能否稳定演进的基础设施。
