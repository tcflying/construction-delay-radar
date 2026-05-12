# Construction Delay Radar AI

建筑工程进度延迟风险预测系统 - MVP

## 核心功能

- 预测项目延迟风险
- 识别关键风险因素
- 生成缓解建议
- E2E自动化验收

## 技术栈

| 组件 | 技术 |
|------|------|
| API | FastAPI 0.104+ |
| ML | XGBoost + Scikit-learn |
| 测试 | Pytest + Playwright |
| 部署 | Docker + GitHub Actions |

## 快速启动

```bash
# 本地开发
cd construction-delay-radar/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 运行测试
python -m pytest tests/test_api.py -v

# Docker部署
cd construction-delay-radar
docker-compose up -d
```

## API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /api/health | 健康检查 |
| POST | /api/projects/ | 创建项目 |
| POST | /api/predict/ | 延迟预测 |
| GET | /api/predict/factors | 风险因素 |

## 验收标准 (E2E)

### 测试通过标准

- [x] TC-001: 健康检查 → 200 OK
- [x] TC-002: 创建项目 → 201 Created
- [x] TC-003: 延迟预测 → 200 OK + 包含预测结果
- [x] TC-004: 无效数据 → 422 Validation Error
- [x] TC-005: 响应时间 → < 2秒

### 当前状态

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.3
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_create_project PASSED
tests/test_api.py::test_predict_delay PASSED
======================== 3 passed in 1.35s =========================
```

## 输入输出示例

### 预测请求
```json
POST /api/predict/
{
  "project_id": "NYC-SCA-2024-001",
  "progress_percent": 35,
  "weather_delays_days": 5,
  "resource_shortage_score": 0.6,
  "supply_chain_score": 0.4,
  "historical_performance": 0.78
}
```

### 预测响应
```json
{
  "project_id": "NYC-SCA-2024-001",
  "predicted_delay_days": 12,
  "confidence": 0.85,
  "risk_level": "MEDIUM",
  "top_factors": [
    {"factor": "weather_delays", "contribution": 3.5},
    {"factor": "resource_shortage", "contribution": 2.8}
  ],
  "recommendations": [
    "提前储备关键材料",
    "增加雨天施工人员"
  ]
}
```

## 项目结构

```
construction-delay-radar/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/    # API路由
│   │   ├── services/         # ML服务
│   │   ├── schemas/          # Pydantic模型
│   │   └── main.py           # FastAPI入口
│   ├── tests/                # 单元测试
│   └── requirements.txt
├── e2e_tests.py              # E2E测试
├── docker-compose.yml
└── Dockerfile
```

## 部署流程

1. PR合并 → 触发CI
2. 运行单元测试
3. 运行E2E测试
4. 通过 → 部署到staging
5. 手动确认 → 部署到生产

## 参考项目

- [CadenHimes/subcontractor-delay-ai](https://github.com/CadenHimes/subcontractor-delay-ai) - AI早期预警
- [EverseDevelopment/e-verse.AIModel.Construction.Schedules](https://github.com/EverseDevelopment/e-verse.AIModel.Construction.Schedules) - 进度ML
- [ClaudeAutoPM](https://github.com/rafeekpro/ClaudeAutoPM) - PM自动化 ⭐29
