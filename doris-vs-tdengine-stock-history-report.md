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

## 13. 历史数据从哪里获取

如果这个系统是为了真正做股票分析和量化挖掘，数据源不能只靠一个渠道。更稳妥的做法是分成三层：

- **官方/授权源**：用于保证口径、合规性和关键数据可信度
- **工程接口源**：用于快速接入、批量同步、缩短研发周期
- **补充与校验源**：用于缺口补数、交叉校验、降低单点故障风险

### 13.1 建议的数据源分层

#### A. 官方/授权源

适合作为生产环境的“准主源”：

- **交易所与官方数据服务**
  - 上交所官网可获取股票成交概况、部分历史统计数据  
    来源：<https://www.sse.com.cn/market/stockdata/overview/day/>
  - 中国投资信息有限公司历史数据页面明确说明：上交所、中证指数、中金所历史数据可由其平台获取，且数据由官方直接提供  
    来源：<https://www.ciis.com.hk/hongkong/sc/historicaldata1/index.shtml>
  - 港交所提供历史数据的程序化下载接口，适合港股或跨市场扩展  
    来源：<https://www.hkex.com.hk/-/media/HKEX-Market/Global/Exchange/FAQ/Market-Data/Getting-Market-Data/Historical-Data/Programmatic-Download-API-Interface-Specification-v1%2C-d-%2C0.pdf>
- **法定信息披露平台**
  - 巨潮资讯网是深交所法定信息披露平台，适合抓取公告、年报、季报、临时公告、问询回复等文本数据  
    来源：<https://www.cninfo.com.cn/new/index>
  - 中国证监会也明确过创业板法定信息披露网站为 `cninfo.com.cn`  
    来源：<https://www.csrc.gov.cn/csrc/c100028/c1002699/content.shtml>
- **指数与成分数据**
  - 中证指数公司提供指数、成分、主题指数、行业指数等服务，适合指数增强、行业轮动、基准对比  
    来源：<https://www.csindex.com.cn/>

这一层的特点是：**口径稳、可信度高、适合生产，但接入成本和授权成本通常更高。**

#### B. 工程接口源

适合作为研发阶段主力来源，或生产中的标准化接入层：

- **Tushare Pro**
  - 支持 A 股日线、股票基础信息、财务报表等接口，适合统一抓取  
    来源：<https://tushare.pro/document/2?doc_id=27>  
    来源：<https://tushare.pro/document/2?doc_id=25>  
    来源：<https://tushare.pro/document/2?doc_id=33>
  - 官方还提供“数据库本地同步服务”和金融数据库落地方案说明，说明它本身就是面向本地量化数据库建设的工程型产品  
    来源：<https://www.tushare.pro/document/search>
- **AKShare**
  - 覆盖市场广、接入快、适合原型验证和补充抓取  
    来源：<https://akshare.akfamily.xyz/>
  - 但官方声明写得很清楚：**仅用于学术研究，不可做商业用途**  
    来源：<https://akshare.akfamily.xyz/special.html>

这一层的特点是：**开发效率高、上手快，但需要自己承担稳定性、授权边界和字段口径治理。**

#### C. 商业数据源

如果目标是机构级研究系统，通常还会引入：

- `Wind`
- `Choice`
- `iFinD`
- 交易所授权行情服务商

这一层适合解决：

- 更完整的分钟线 / Tick / L2
- 更稳定的财务与一致预期数据
- 机构持仓、卖方预期、行业口径映射
- 商业授权与 SLA

如果你的目标是“自己做一个高质量研究系统”，但还不是券商/私募生产环境，比较现实的路径通常是：

- **起步版**：`Tushare Pro + 巨潮资讯 + 交易所公开数据`
- **增强版**：`Tushare Pro + 官方授权数据 + 公告文本抽取`
- **机构版**：`官方/授权主源 + 商业数据 + 自建清洗校验链路`

### 13.2 按数据主题拆解，分别从哪里取

建议不要按“供应商”建系统，而要按“数据主题”建系统：

- **证券主数据**
  - 股票代码、简称、上市退市、交易所、板块、行业分类
  - 推荐来源：`Tushare stock_basic` + 交易所官网 + 自建主数据表
- **历史行情**
  - 日线、分钟线、Tick、成交量、成交额、复权前原始价
  - 推荐来源：`Tushare daily` 做日线，分钟/Tick 优先官方授权或商业源
- **复权与公司行为**
  - 分红送转、配股、拆并股、停复牌、特别处理
  - 推荐来源：交易所公告 + 巨潮资讯 + 数据商标准化结果
- **财务数据**
  - 三大报表、财务指标、现金流、盈利能力、杠杆、成长性
  - 推荐来源：`Tushare income/balance/cashflow/financial indicators` + 巨潮原始公告
- **公告与文本**
  - 年报、季报、业绩预告、回购、减持、问询函、回复函、投资者关系纪要
  - 推荐来源：`cninfo`
- **指数与行业**
  - 沪深300、中证500、中证1000、行业分类、指数成分与调样
  - 推荐来源：中证指数公司
- **资金行为**
  - 北向资金、龙虎榜、融资融券、大宗交易、股东增减持
  - 推荐来源：Tushare / 官方披露 / 商业数据源
- **新闻与舆情**
  - 财经新闻、研报、社媒情绪、公告摘要
  - 推荐来源：商业资讯源、自建 NLP 抽取链路

### 13.3 最务实的数据接入建议

如果你现在就要开工，我建议分三步：

1. **先把日线、主数据、财务、公告跑通**
   - 这是性价比最高的一层，足够支持大部分中低频量化研究
2. **再补分钟线和事件标签**
   - 分钟线用于短中周期择时，事件标签用于事件驱动研究
3. **最后再决定是否引入 Tick / L2**
   - 这部分成本和复杂度会陡增，不应该在系统 0 到 1 阶段过早背上

换句话说，真正高价值的量化系统，不一定一开始就需要最贵、最细的数据；更重要的是**数据口径稳定、可追溯、可回放、可复现实验**。

## 14. 如何做一个高价值量化挖掘分析系统

如果基于当前这个场景来设计，我不建议把它做成“行情库存储系统”，而应该做成一个**研究驱动的量化分析系统**。  
它的目标不是“把数据存进去”，而是持续回答下面几类问题：

- 哪些信号在不同市场环境下有效？
- 哪些 alpha 来自基本面，哪些来自资金行为，哪些来自事件与文本？
- 哪些策略只是样本内有效，哪些具备跨周期稳定性？
- 哪些因子有真实可交易性，而不是回测幻觉？

### 14.1 推荐的总体架构

#### 第一层：数据采集层

负责把多源数据标准化拉下来：

- `batch ingest`：日线、财务、公告、指数成分、交易日历
- `stream ingest`：分钟线、Tick、盘口、实时事件
- 原始数据全部落到对象存储或原始库，保留 `source`、`ingest_time`、`version`

建议原则：

- 原始数据永不覆盖，只追加版本
- 所有修正都在标准层做，不在原始层偷偷改
- 每条记录尽量保留来源和抓取批次

#### 第二层：标准化与数仓层

这里建议以 **Doris 为主仓**，按典型数仓分层：

- `ODS`：原始落地后的标准化表
- `DWD`：清洗后的明细层，例如 `dwd_bar_1d`、`dwd_fin_income`、`dwd_announcement`
- `DWS`：主题汇总层，例如 `dws_symbol_daily_snapshot`、`dws_industry_daily`
- `ADS`：面向研究/API/BI 的应用层宽表

如果有高频实时需求，再加一个 **TDengine 侧车**：

- `TDengine`：接 Tick、盘口、实时窗口计算
- `Doris`：接标准化结果、复权结果、因子结果、研究查询

这和前面的选型结论是一致的：**Doris 做主研究仓，TDengine 做高频子系统。**

### 14.2 核心数据模型

至少建议建这些主题表：

- `dim_symbol`
- `dim_calendar`
- `dim_industry`
- `dim_index_constituent`
- `fact_bar_1d`
- `fact_bar_1m`
- `fact_tick`
- `fact_corporate_action`
- `fact_financial_statement`
- `fact_announcement`
- `fact_capital_flow`
- `fact_margin_trading`
- `fact_block_trade`
- `fact_factor_exposure`
- `fact_alpha_signal`
- `fact_backtest_trade`
- `fact_strategy_nav`

真正高价值的地方不在“表多”，而在下面三个统一：

- **统一证券主键**
- **统一交易日历**
- **统一时间口径与复权口径**

只要这三件事不统一，后面的因子和回测几乎都会持续出错。

### 14.3 高价值量化挖掘，不该只盯技术指标

如果系统只做 MA、MACD、KDJ、RSI，这个系统的上限会很低。  
更高价值的 alpha 往往来自多源组合：

- **价格行为类**
  - 动量、反转、波动率收缩、跳空、趋势斜率、量价背离
- **横截面因子类**
  - 估值、盈利质量、成长性、杠杆、现金流、分红、低波、质量
- **资金行为类**
  - 北向资金、融资融券、龙虎榜、主力净流入、大宗交易
- **事件驱动类**
  - 财报披露、业绩预告、回购、减持、重大合同、监管问询、并购重组
- **文本/NLP 类**
  - 年报文本情绪、管理层措辞变化、问询函风险强度、新闻主题漂移
- **微观结构类**
  - Tick 不平衡、盘口压力、成交簇、尾盘行为、开盘冲击

真正容易做出差异化价值的，通常不是单一因子，而是：

- `基本面因子 + 事件标签`
- `资金行为 + 横截面排序`
- `公告文本信号 + 后续收益分布`
- `行业轮动 + 风格暴露控制`

### 14.4 研究引擎应该怎么做

系统里至少要有 5 个研究模块：

#### 1. 因子工厂

负责批量生成和管理因子：

- 因子定义版本化
- 支持前复权/后复权/不复权切换
- 支持按交易日回放
- 支持因子血缘追踪

#### 2. 标签工厂

负责生成研究目标：

- 未来 1/5/20/60 日收益
- 超额收益
- 最大回撤
- 胜率
- 波动调整后收益

没有统一标签工厂，研究结果会不可比。

#### 3. 回测与验证层

至少做这些校验：

- 因子 IC / RankIC
- 分层回测
- 换手率
- 容量约束
- 滑点与交易成本
- 牛熊市分段表现
- 样本外验证
- 滚动训练 / 滚动验证

#### 4. 风险归因层

负责回答“你赚的钱到底来自什么”：

- 行业暴露
- 市值暴露
- 风格暴露
- Beta 暴露
- 事件集中度
- 持仓拥挤度

#### 5. 服务与可视化层

用于把研究能力变成可消费产品：

- Superset / BI 看板
- FastAPI 查询服务
- 因子筛选接口
- 策略监控报表
- 研究员自助 SQL

### 14.5 这个系统里最值钱的几类成果

如果做得好，真正值钱的不是“数据库本身”，而是以下资产：

- **可持续维护的因子库**
- **可复现实验框架**
- **事件标签与文本特征库**
- **统一的证券研究宽表**
- **跨周期可比较的回测与监控体系**

这些东西一旦建立起来，你后面新增一个策略，不再是重新造轮子，而是复用已有底座。

### 14.6 一套务实的落地路线图

#### 阶段 1：先做可用

- 接入 `Tushare Pro + 巨潮资讯`
- 建 `dim_symbol`、`fact_bar_1d`、`fact_financial_statement`、`fact_announcement`
- 在 Doris 内形成基础宽表
- 跑通最基础的横截面选股与事件研究

#### 阶段 2：再做有效

- 引入分钟线、资金行为数据
- 建因子工厂、标签工厂、回测框架
- 做行业中性、市值中性、交易成本修正
- 开始筛掉大多数伪 alpha

#### 阶段 3：最后做壁垒

- 引入公告 NLP、研报摘要、新闻主题、管理层措辞变化
- 叠加事件驱动与基本面质量因子
- 建立组合归因、容量分析、实时监控
- 把研究结果产品化成 API / 看板 / 策略服务

### 14.7 基于当前选型的最终工程建议

如果只选一个主库，我仍然建议：

- **主仓：Doris**
- **高频侧车：TDengine（可选）**
- **计算层：Python + SQL 为主，必要时补 Spark/Flink**
- **对象存储：保存原始行情、公告 PDF、文本抽取结果**
- **服务层：Superset + FastAPI**

原因很直接：

- 你的核心目标不是“存一堆时序”
- 而是“把多源证券数据组织成可研究、可验证、可迭代的 alpha 工厂”

对这个目标来说，**Doris 更像中枢；TDengine 更像专项加速器。**
