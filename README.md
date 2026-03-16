# 💰 资金追踪系统

一个基于 Streamlit 的个人资金追踪网站，帮助你实时掌握资产动态。

## 功能特性

- **仪表盘** - 总资产、平台数、账户数、今日变动一览
- **图表可视化** - 饼图、柱状图、趋势图展示资金分布
- **资金管理** - 添加/编辑/删除资金记录，支持备注
- **变动历史** - 自动记录每次金额变化，支持筛选
- **统计报表** - 月度汇总、平台对比、CSV导出
- **自定义设置** - 管理平台和渠道类型

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
streamlit run app.py
```

应用将在 http://localhost:8501 启动

## 项目结构

```
funds_tracker/
├── app.py              # 主页仪表盘
├── data_manager.py     # 数据管理模块
├── requirements.txt    # 依赖
├── data/               # 数据存储
│   ├── accounts.json   # 平台和渠道配置
│   ├── funds.json      # 资金记录
│   └── history.json    # 变动历史
└── pages/
    ├── 1_资金管理.py
    ├── 2_变动历史.py
    ├── 3_统计报表.py
    └── 4_设置.py
```

## 预置平台

- 支付宝 💳
- 微信 💚
- 工商银行 🏦
- 建设银行 🏛️
- 中信证券 📈
- 现金 💵

## 预置渠道类型

- 活期
- 定期
- 理财
- 股票
- 其他

## 技术栈

- Python 3.14
- Streamlit
- Plotly

## License

MIT