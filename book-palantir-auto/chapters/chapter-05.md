# 第5章：数据标准化与建模

## 本章要点

- 企业级数据模型设计
- 主数据管理
- 数据标准化规范
- Palantir Ontology建模

---

## 5.1 企业级数据模型设计

### 5.1.1 建模方法论

**业界主流方法**：

| 方法 | 特点 | 适用场景 |
|------|------|---------|
| Kimball维度建模 | 面向分析，性能优化 | 数据仓库、BI |
| Inmon范式建模 | 面向业务，一致性 | 交易系统 |
| Data Vault | 面向集成，可追溯 | 大数据集成 |

**推荐方案**：汽车主机厂建议采用混合架构

- 交易层采用范式建模（3NF）
- 分析层采用维度建模
- 集成层采用Data Vault

### 5.1.2 模型层次架构

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层（Applications）                 │
│   报表/仪表盘 | 数据应用 | 自助分析 | API服务               │
├─────────────────────────────────────────────────────────────┤
│                      分析层（Analytics）                    │
│   汇总表 | 指标库 | 分析模型 | 机器学习                     │
├─────────────────────────────────────────────────────────────┤
│                      整合层（Integration）                  │
│   统一视图 | 数据清洗 | 数据转换 | 数据关联                 │
├─────────────────────────────────────────────────────────────┤
│                      源数据层（Source）                      │
│   ERP | MES | PLM | QMS | CRM | 其他系统                   │
└─────────────────────────────────────────────────────────────┘
```

### 5.1.3 核心主题域模型

**1. 客户主题域**

```
Customer (客户)
├── Customer_ID (客户ID)
├── Customer_Type (客户类型)
├── Customer_Name (客户名称)
├── Customer_Status (客户状态)
├── Create_Date (创建日期)
└── ... (其他属性)

Customer_Address (客户地址)
├── Address_ID (地址ID)
├── Customer_ID (客户ID)
├── Address_Type (地址类型)
├── Province (省份)
├── City (城市)
├── District (区县)
├── Detail_Address (详细地址)
└── ...

Customer_Contact (客户联系人)
├── Contact_ID (联系人ID)
├── Customer_ID (客户ID)
├── Contact_Name (联系人姓名)
├── Contact_Role (联系人角色)
├── Phone (电话)
├── Email (邮箱)
└── ...
```

**2. 产品主题域**

```
Product (产品)
├── Product_ID (产品ID)
├── Product_Code (产品编码)
├── Product_Name (产品名称)
├── Product_Category (产品类别)
├── Product_Series (产品系列)
├── Brand (品牌)
├── Model (车型)
├── Year (年款)
├── Color (颜色)
└── ...

Product_BOM (产品BOM)
├── BOM_ID (BOM_ID)
├── Product_ID (父产品ID)
├── Component_ID (子件ID)
├── Quantity (数量)
├── Unit (单位)
├── Valid_From (生效日期)
└── Valid_To (失效日期)
```

**3. 订单主题域**

```
Sales_Order (销售订单)
├── Order_ID (订单ID)
├── Order_No (订单号)
├── Customer_ID (客户ID)
├── Order_Date (订单日期)
├── Order_Status (订单状态)
├── Total_Amount (订单金额)
├── Delivery_Date (交货日期)
└── ...

Order_Line (订单行)
├── Line_ID (行ID)
├── Order_ID (订单ID)
├── Product_ID (产品ID)
├── Quantity (数量)
├── Unit_Price (单价)
├── Amount (金额)
├── Delivery_Date (交货日期)
└── ...
```

---

## 5.2 主数据管理

### 5.2.1 主数据概述

**主数据定义**：主数据是描述企业核心业务实体的数据，如客户、产品、供应商、员工等。这些数据在多个业务系统中共享使用。

**汽车主机厂核心主数据**：

| 主数据类型 | 典型属性 | 使用系统 |
|-----------|---------|---------|
| 物料主数据 | 编码、名称、规格、单位 | ERP/MES/PLM |
| 客户主数据 | 编码、名称、联系人、地址 | ERP/CRM |
| 供应商主数据 | 编码、名称、联系人、资质 | ERP/QMS |
| 员工主数据 | 工号、姓名、部门、岗位 | ERP/HR |
| 设备主数据 | 编码、名称、型号、位置 | MES/EAM |
| 车型主数据 | 编码、名称、配置、年款 | ERP/PLM/MES |

### 5.2.2 主数据管理流程

```
┌─────────────────────────────────────────────────────────────┐
│                      主数据管理流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │ 申请     │───▶│ 审核     │───▶│ 发布     │            │
│   │(Create)  │    │(Approve) │    │(Publish) │            │
│   └──────────┘    └──────────┘    └──────────┘            │
│                                             │               │
│                                             ▼               │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │ 归档     │◀───│ 变更     │◀───│ 分发     │            │
│   │(Archive) │    │(Change)  │    │(Distribute)│           │
│   └──────────┘    └──────────┘    └──────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**关键流程说明**：

1. **申请**：业务部门提交主数据创建/变更申请
2. **审核**：主数据管理委员会审批
3. **发布**：将批准的主数据发布到主数据库
4. **分发**：将主数据同步到各业务系统
5. **变更**：主数据发生变化时触发变更流程
6. **归档**：历史变更记录归档保存

### 5.2.3 主数据治理规则

**1. 编码规则**

| 主数据 | 编码规则 | 示例 |
|--------|---------|------|
| 物料 | 类别(2位)+流水号(6位) | MP000001 |
| 客户 | C+流水号(8位) | C00000001 |
| 供应商 | S+流水号(8位) | S00000001 |
| 设备 | E+产线(2位)+流水号(4位) | E010001 |
| 车型 | 品牌+系列+年款 | BYD-Dolphin-2024 |

**2. 唯一性规则**

- 同一企业内，主数据编码不允许重复
- 关键字段组合唯一（如：客户+渠道）
- 自动查重校验

**3. 完整性规则**

- 必填字段不能为空
- 关联字段必须存在
- 格式必须符合规范

---

## 5.3 数据标准化规范

### 5.3.1 命名规范

**数据库对象命名**：

| 对象类型 | 命名规则 | 示例 |
|---------|---------|------|
| 数据库 | 小写+下划线 | palantir_auto |
| 表 | 主题域_业务对象 | dim_product |
| 视图 | v_业务对象 | v_sales_order |
| 字段 | 小写+下划线 | customer_name |
| 主键 | pk_表名 | pk_dim_product |
| 外键 | fk_表名_关联表 | fk_order_customer |

**字段命名缩写**：

| 缩写 | 全写 | 说明 |
|------|------|------|
| id | identifier | 标识符 |
| no | number | 编号 |
| nm | name | 名称 |
| dt | date | 日期 |
| qty | quantity | 数量 |
| amt | amount | 金额 |
| pct | percent | 百分比 |
| tbl | table | 表格 |

### 5.3.2 数据类型规范

| 数据类型 | 使用场景 | 示例 |
|---------|---------|------|
| VARCHAR(n) | 字符串，长度确定 | VARCHAR(50) |
| TEXT | 长文本 | 描述、备注 |
| INT/BIGINT | 整数 | 数量、ID |
| DECIMAL(p,s) | 精确数值 | 金额、重量 |
| DATE | 日期 | 2024-01-01 |
| DATETIME | 日期时间 | 2024-01-01 10:00:00 |
| BOOLEAN | 布尔值 | TRUE/FALSE |
| JSON | JSON数据 | 配置、扩展属性 |

### 5.3.3 编码值规范

**通用状态码**：

| 编码 | 含义 | 使用场景 |
|------|------|---------|
| 00 | 新建 | 新增数据 |
| 01 | 正常 | 正常状态 |
| 02 | 冻结 | 临时停用 |
| 03 | 注销 | 已删除 |
| 04 | 变更 | 待审批 |
| 05 | 过期 | 已失效 |

**业务状态码** - 订单状态：

| 编码 | 含义 |
|------|------|
| PENDING | 待确认 |
| CONFIRMED | 已确认 |
| PRODUCING | 生产中 |
| SHIPPED | 已发货 |
| DELIVERED | 已送达 |
| COMPLETED | 已完成 |
| CANCELLED | 已取消 |

---

## 5.4 Palantir Ontology建模

### 5.4.1 Ontology概念

Palantir的Ontology是其核心概念，它定义了数据的语义模型，是连接物理数据和业务逻辑的桥梁。

**核心元素**：

| 元素 | 说明 | 示例 |
|------|------|------|
| Object Type | 对象类型 | Vehicle, Order, Customer |
| Property | 属性 | Vehicle.vin, Order.quantity |
| Relationship | 关系 | Order→Customer, Vehicle→Order |
| Action | 动作 | CreateOrder, ApproveQuote |
| Repository | 仓库 | 存储Object Type的定义 |

### 5.4.2 汽车行业Ontology示例

**1. 车辆对象**

```json
{
  "objectType": "Vehicle",
  "description": "车辆",
  "properties": [
    {"name": "vin", "type": "string", "description": "车架号", "required": true},
    {"name": "vehicleCode", "type": "string", "description": "车辆编码"},
    {"name": "model", "type": "string", "description": "车型"},
    {"name": "color", "type": "string", "description": "颜色"},
    {"name": "productionDate", "type": "datetime", "description": "生产日期"},
    {"name": "salesDate", "type": "datetime", "description": "销售日期"},
    {"name": "status", "type": "enum", "description": "状态", 
     "values": ["WIP", "Stock", "Sold", "InService"]}
  ],
  "relationships": [
    {"name": "model", "target": "VehicleModel", "type": "many-to-one"},
    {"name": "owner", "target": "Customer", "type": "many-to-one"},
    {"name": "orders", "target": "SalesOrder", "type": "one-to-many"}
  ]
}
```

**2. 订单对象**

```json
{
  "objectType": "SalesOrder",
  "description": "销售订单",
  "properties": [
    {"name": "orderNo", "type": "string", "description": "订单号", "required": true},
    {"name": "orderDate", "type": "datetime", "description": "订单日期"},
    {"name": "quantity", "type": "integer", "description": "数量"},
    {"name": "amount", "type": "decimal", "description": "订单金额"},
    {"name": "status", "type": "enum", "description": "状态",
     "values": ["Draft", "Pending", "Confirmed", "Producing", "Shipped", "Delivered", "Completed", "Cancelled"]}
  ],
  "relationships": [
    {"name": "customer", "target": "Customer", "type": "many-to-one"},
    {"name": "vehicle", "target": "Vehicle", "type": "many-to-one"},
    {"name": "dealer", "target": "Dealer", "type": "many-to-one"}
  ]
}
```

**3. 质量检验对象**

```json
{
  "objectType": "QualityInspection",
  "description": "质量检验",
  "properties": [
    {"name": "inspectionId", "type": "string", "description": "检验单号", "required": true},
    {"name": "inspectionType", "type": "enum", "description": "检验类型",
     "values": ["IPQC", "FQC", "OQC"]},
    {"name": "result", "type": "enum", "description": "检验结果",
     "values": ["Pass", "Fail", "Rework"]},
    {"name": "defectCount", "type": "integer", "description": "缺陷数量"},
    {"name": "inspector", "type": "string", "description": "检验员"},
    {"name": "inspectionTime", "type": "datetime", "description": "检验时间"}
  ],
  "relationships": [
    {"name": "vehicle", "target": "Vehicle", "type": "many-to-one"},
    {"name": "station", "target": "WorkStation", "type": "many-to-one"},
    {"name": "defects", "target": "QualityDefect", "type": "one-to-many"}
  ]
}
```

### 5.4.3 Ontology设计最佳实践

**1. 渐进式建模**

- 从核心业务对象开始
- 逐步扩展到周边对象
- 持续迭代优化

**2. 业务导向**

- 以业务视角建模，而非技术视角
- 关注业务实体和关系
- 抽象共性，保留个性

**3. 可追溯性**

- 记录数据血缘
- 追踪数据来源
- 审计数据变更

**4. 权限控制**

- 基于对象类型设置访问权限
- 基于属性设置敏感度
- 基于关系控制数据访问

---

## 5.5 本章小结

本章介绍了数据标准化与建模的方法。

**本章要点回顾**：

1. 企业级数据模型需要分层设计，包括源数据层、整合层、分析层、应用层
2. 主数据管理是数据治理的核心，需要建立完善的管理流程和治理规则
3. 数据标准化规范包括命名规范、类型规范、编码规范
4. Palantir通过Ontology实现语义建模，核心元素包括Object Type、Property、Relationship、Action

---

## 思考题

1. 你的企业主数据管理现状如何？存在哪些问题？
2. 数据标准化遇到最大的挑战是什么？如何解决？
3. Palantir Ontology与传统的ER模型有什么区别？

---

*下章预告：第6章将介绍主数据管理的详细实施方案*