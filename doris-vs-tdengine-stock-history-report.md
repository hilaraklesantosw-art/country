# 使用 Doris 分析股票历史数据 vs 使用 TDengine 分析股票历史数据

## 1. 报告结论

如果目标是搭建一个**面向股票历史数据的长期分析平台**，我更建议优先选择 **Apache Doris** 作为主分析引擎。  
如果目标是搭建一个**以高频时序写入、时间窗口聚合、实时流处理为主**的窄场景系统，**TDengine** 也可行，但更适合作为时序子系统，而不是整个平台唯一核心数据库。

一句话结论：

- **主推荐**：`Doris`
- **条件推荐**：`TDengine` 仅在“纯时序、少维表、少复杂 join、强调实时流和时间窗口计算”的场景下更合适
- **最稳妥架构**：`Doris 作为主分析仓 + TDengine 作为实时时序侧车`，但如果只能选一个，优先 `Doris`

我的判断是一个**面向股票历史数据的完整系统判断**，不是单看数据库单项性能。

## 2. 背景假设

这里默认“股票历史数据分析”不只是存 K 线，而是包含以下典型能力：

- 日线、分钟线、逐笔/Tick、成交量、成交额、盘口等历史行情
- 复权处理、停牌/除权除息/交易日历
- 多标的横截面对比
- 技术指标、因子计算、板块聚合、策略回测前置分析
- 与财务数据、公告、新闻、行业分类、指数成分等维表联查
- BI 报表、临时 SQL、研究分析、API 服务

如果你的真实需求只是不停写入时序行情，然后做简单窗口聚合，那结论会更偏向 TDengine；但如果是“研究分析平台”，结论会明显偏向 Doris。

## 3. 评估维度

本报告用以下维度比较：

1. 数据模型适配度
2. 历史行情查询能力
3. 多表关联与横截面分析能力
4. 实时写入与增量更新
5. 物化汇总和预计算能力
6. BI / SQL / 生态兼容性
7. 运维复杂度与长期演进风险
8. 对股票场景的总体适配性

## 4. 官方能力对比

### 4.1 Doris 的官方定位

Apache Doris 官方将自己定义为 **MPP-based real-time data warehouse**，强调：

- 大数据集上的亚秒级查询
- 高并发点查与高吞吐复杂分析
- 报表分析、ad-hoc 查询、统一数仓、Lakehouse 加速
- 标准 SQL、MySQL 协议兼容、BI 工具兼容  
  来源：<https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>

官方还明确给出：

- 支持多源联邦分析
- 支持宽表、星型/雪花模型、视图、物化视图、实时多表 join
- 支持多种数据模型：Duplicate Key、Unique Key、Aggregate Key
- 支持 Kafka/Flink CDC/Stream Load/Routine Load 等导入方式  
  来源：<https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>  
  来源：<https://doris.apache.org/docs/dev/data-operate/import/load-manual/>

这说明 Doris 的强项不是“单一时序引擎”，而是**通用分析型平台**。

### 4.2 TDengine 的官方定位

TDengine 官方将自己定义为 **专为时序数据设计的高性能 TSDB**，强调：

- 时序数据的高性能写入、查询、压缩
- 一个数据采集点一张表、超级表模型
- 内建缓存、流式计算、数据订阅
- 支持时间加权平均、降采样、插值等时序扩展函数  
  来源：<https://docs.taosdata.com/>  
  来源：<https://docs.taosdata.com/intro/>

官方还写得很直接：

- TDengine 适合 IoT、工业互联网、车联网、金融证券、IT 运维等场景
- 但**需要大量交叉查询处理**的场景，更应该用关系型数据库处理，或和关系型数据库配合  
  来源：<https://docs.taosdata.com/intro/>

这句话对股票历史分析非常关键。因为股票研究分析里，“跨标的、跨时间、跨维表”的交叉查询是常态，而不是例外。

## 5. 针对股票历史数据的实际比较

### 5.1 数据模型适配度

#### Doris

适合把股票系统建成：

- `fact_bar_1m` / `fact_bar_1d` 行情事实表
- `fact_tick` 逐笔表
- `dim_symbol` 股票维表
- `dim_calendar` 交易日历
- `dim_industry` 行业分类
- `dim_corporate_action` 复权事件
- `fact_factor` 因子结果表

这种建模方式和证券研究、量化分析、BI 报表习惯一致。

#### TDengine

TDengine 的设计中心是“一个采集点一张表 + 超级表”。  
对于股票数据，这通常意味着：

- 每只股票一个子表
- 时间戳是主轴
- 股票属性放在 tag

这对“按时间写入单标的行情”是自然的，但对下面这些操作就不自然：

- 大量股票横截面对比
- 复杂维表 join
- 复权、行业、财务、公告等多域数据联合分析
- 面向研究员的宽 SQL 分析

结论：**股票研究型建模，Doris 更顺手。**

### 5.2 历史行情查询与时间序列分析

#### TDengine 优势

TDengine 原生就是 TSDB，官方强调：

- 时间窗口聚合
- 降采样
- 时间加权平均
- 流计算
- 数据订阅  
  来源：<https://docs.taosdata.com/>  
  来源：<https://docs.taosdata.com/intro/>  
  来源：<https://docs.taosdata.com/cloud/stream/>

如果你的核心查询是：

- 某只股票最近 N 天分钟线聚合
- 实时写入 Tick 后立即做窗口计算
- 订阅最新数据推送策略引擎

TDengine 很有吸引力。

#### Doris 优势

Doris 虽不是专用 TSDB，但它是分析型数仓：

- 列存
- MPP
- 向量化执行
- 复杂 SQL
- 物化视图
- 分区与自动分区
- 原始表与聚合表并存  
  来源：<https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>  
  来源：<https://doris.apache.org/docs/3.x/table-design/data-partitioning/auto-partitioning/>

这使它非常适合：

- 多年历史行情查询
- 多标的聚合
- 板块、行业、指数成分聚合
- 因子批量计算
- 研究型 ad-hoc SQL

结论：**纯时序窗口处理 TDengine 更原生，综合历史分析 Doris 更强。**

### 5.3 多表关联与横截面分析

这是两者最关键的分水岭。

股票分析里经常会写出这样的查询：

- 某日全市场 PE 排名前 200 的股票，叠加过去 60 日收益率和成交额
- 某板块成分股过去 3 年月度收益分布
- 除权后复权价序列和财务指标联查
- 事件驱动研究：公告日后 5/20/60 日收益

这类需求高度依赖：

- 多表 join
- 复杂过滤
- 宽表/星型模型
- 批量聚合
- 物化结果复用

Apache Doris 官方明确支持：

- 多表 join
- 星型/雪花模型
- 物化视图
- 多源联邦分析  
  来源：<https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>  
  来源：<https://doris.apache.org/docs/dev/lakehouse/lakehouse-overview/>

TDengine 官方则明确提醒：

- 大量交叉查询更适合关系型数据库，或与关系型数据库配合  
  来源：<https://docs.taosdata.com/intro/>

结论：**横截面与多域联查，Doris 明显更靠谱。**

### 5.4 实时写入与更新

#### Doris

官方支持：

- JDBC / HTTP 实时写入
- Kafka、Flink、CDC 等实时同步
- Unique Key UPSERT
- Partial Column Update  
  来源：<https://doris.apache.org/docs/dev/data-operate/import/load-manual/>  
  来源：<https://doris.apache.org/docs/4.x/table-design/data-model/unique/>

这意味着它适合做：

- 实时分钟线/日线增量同步
- 证券主数据更新
- 因子、信号、标签表增量覆盖

#### TDengine

TDengine 在实时写入上原生很强，尤其适合：

- 高频连续写入
- 流式计算
- 订阅最新数据  
  来源：<https://docs.taosdata.com/intro/>  
  来源：<https://docs.taosdata.com/cloud/stream/>  
  来源：<https://docs.taosdata.com/cloud/data-subscription/>

结论：**极高频原始时序写入 TDengine 更原生；带更新语义的综合分析系统 Doris 更均衡。**

### 5.5 预聚合与加速

#### Doris

官方强调：

- 单表物化视图自动维护
- 多表物化视图支持周期刷新、分区级增量刷新、数据驱动刷新  
  来源：<https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>  
  来源：<https://doris.apache.org/docs/dev/lakehouse/lakehouse-overview/>

这非常适合股票场景里的：

- 日线汇总
- 周/月聚合
- 板块快照
- 因子宽表
- 常用筛选结果预计算

#### TDengine

TDengine 更偏向：

- 流计算
- 时间窗口聚合
- 时序预处理  
  来源：<https://docs.taosdata.com/cloud/stream/>

它能做实时窗口汇总，但对“多主题、多表、多维分析的物化层”没有 Doris 那么自然。

结论：**分析型预聚合 Doris 更适合。**

### 5.6 BI 与研究生态

#### Doris

官方采用 MySQL 协议并强调标准 SQL 与 BI 兼容。  
来源：<https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>

这对股票分析尤其重要，因为研究、投研、运营、产品团队常常直接接：

- Superset
- Tableau
- Power BI
- DataEase
- 自研 MySQL 生态工具

#### TDengine

TDengine 也支持 BI 集成，官方提供了 Superset、Excel、Spark 等接入说明。  
来源：<https://docs.taosdata.com/third-party/bi/superset/>  
来源：<https://docs.taosdata.com/third-party/bi/excel/>  
来源：<https://docs.taosdata.com/third-party/bi/spark/>

但其核心生态重心仍然是“时序平台”，不是“证券研究数仓”。

结论：**两者都能接 BI，但 Doris 更贴近通用分析平台。**

## 6. 关键判断：哪一个更靠谱

### 6.1 如果你要的是“股票历史数据分析平台”

更靠谱的是 **Doris**。

原因不是 Doris 在所有单点指标上都更强，而是它更适合股票历史数据分析的真实工作负载：

- 多表 join 多
- 横截面分析多
- 宽表、因子、事件研究多
- BI、研究、API 混合负载多
- 需要持续迭代新主题和新口径

TDengine 在“时间序列数据库”这个子问题上很强，但股票历史分析不是只有时间序列。

### 6.2 如果你要的是“行情时序落库 + 实时窗口计算”

TDengine 也靠谱，甚至可能更省事。

典型场景：

- 只存 Tick/Bar
- 只按 symbol + time 查询
- 主要做 rolling window、降采样、订阅
- 很少与财务、事件、行业等多域数据联查

但一旦需求开始扩展到投研分析，TDengine 的模型边界会更早暴露出来。

## 7. 推荐方案

### 方案 A：只选一个库

优先选择 **Apache Doris**。

推荐理由：

- 更适合完整证券分析平台
- 支持多维聚合和复杂 SQL
- 更适合做研究、报表、API 统一底座
- 对后续接入财务、公告、新闻、行业、因子更友好

### 方案 B：双引擎

如果你有足够团队能力，推荐：

- `TDengine`：接实时 Tick / 高频序列 / 流式窗口
- `Doris`：承接标准化历史行情、复权结果、因子、维表、研究分析、BI、服务 API

这是技术上更完整的架构，但复杂度更高。

### 方案 C：TDengine 单库

仅在下列条件同时满足时推荐：

- 核心目标是时序写入与查询
- join 很少
- 横截面分析较少
- 不追求复杂研究型 SQL
- 团队愿意把复杂分析外移到 Spark / 应用层

否则长期大概率会二次迁移。

## 8. 风险与边界

### Doris 的风险

- 对纯高频 Tick 海量写入，不一定是最原生的 TSDB 方案
- 需要做好表设计、分区、物化视图、冷热分层规划
- 如果拿它直接替代所有流式时序计算，会增加建模工作

### TDengine 的风险

- 股票场景里大量“交叉查询”是硬需求，而官方已明确提示这类处理更适合关系型系统或组合方案
- 一旦接入复权、财务、事件、行业、公告、策略回测结果，模型复杂度会明显上升
- 研究分析平台后期容易演变成“时序库 + 外部分析层”的补丁架构

## 9. 最终建议

### 最终建议

如果你的目标是：

- 建股票历史数据库
- 提供多标的分析
- 做因子研究
- 做板块/行业/指数比较
- 做 BI 报表与 API
- 未来还要接财务、公告、新闻等数据

**请选择 Apache Doris。**

如果你的目标只是：

- 写入大量行情时序
- 做窗口聚合
- 做实时订阅
- 单表或少维度分析为主

**TDengine 可以作为专用时序引擎，但不建议单独承担整个股票历史分析平台。**

## 10. 我的最终判断

### 哪一个更靠谱？

**对“股票历史数据分析”这个完整命题，Doris 更靠谱。**

### 为什么？

因为股票历史数据系统本质上是：

- `时序问题` + `分析型数仓问题` + `多维联查问题` + `研究平台问题`

TDengine 更擅长第一个子问题。  
Doris 更能覆盖整个问题。

## 11. 官方资料来源

- Apache Doris Overview: <https://doris.apache.org/docs/2.1/gettingStarted/what-is-apache-doris/>
- Apache Doris Loading Overview: <https://doris.apache.org/docs/dev/data-operate/import/load-manual/>
- Apache Doris Unique Key Table: <https://doris.apache.org/docs/4.x/table-design/data-model/unique/>
- Apache Doris Duplicate Key Table: <https://doris.apache.org/docs/4.x/table-design/data-model/duplicate/>
- Apache Doris Lakehouse Overview: <https://doris.apache.org/docs/dev/lakehouse/lakehouse-overview/>
- Apache Doris Auto Partitioning: <https://doris.apache.org/docs/3.x/table-design/data-partitioning/auto-partitioning/>
- TDengine 文档首页: <https://docs.taosdata.com/>
- TDengine 产品简介: <https://docs.taosdata.com/intro/>
- TDengine 英文文档首页: <https://docs.tdengine.com/>
- TDengine 流式计算: <https://docs.taosdata.com/cloud/stream/>
- TDengine Superset 集成: <https://docs.taosdata.com/third-party/bi/superset/>
- TDengine Excel 集成: <https://docs.taosdata.com/third-party/bi/excel/>
- TDengine Spark 集成: <https://docs.taosdata.com/third-party/bi/spark/>

## 12. 补充说明

本报告没有采用厂商自报 benchmark 直接判胜负，因为当前没有看到一组针对“股票历史分析”工作负载、且由同一测试口径给出的官方对等对比数据。  
因此本报告的结论主要基于：

- 官方产品定位
- 官方数据模型与能力边界
- 官方对适用/不适用场景的明示
- 对证券分析系统真实工作负载的工程推断

其中“Doris 更适合作为股票历史分析主平台”属于**基于官方能力边界和证券场景特征做出的工程判断**。
