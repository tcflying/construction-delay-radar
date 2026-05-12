# Construction Delay Radar AI - MVP 工作流

## 核心功能
预测建筑工程进度延迟风险，提前预警

## 技术栈

| 层级 | 技术选型 | 版本 |
|------|---------|------|
| 前端 | Streamlit | 1.28+ |
| 后端 | FastAPI | 0.104+ |
| ML模型 | XGBoost + Scikit-learn | 2.0+ / 1.3+ |
| 数据库 | SQLite (MVP) / PostgreSQL (Prod) | - |
| E2E测试 | Playwright | 1.40+ |
| CI/CD | GitHub Actions | - |
| 架构 | Hexagonal (Ports & Adapters) | - |

## MVP 数据流

```
输入数据 → 特征工程 → XGBoost预测 → 延迟风险评分 → Streamlit UI
    ↓
GitHub Actions (CI/CD) → Playwright E2E验证 → 部署
```

## 输入样例 (JSON)

```json
{
  "project_id": "NYC-SCA-2024-001",
  "project_name": "Brooklyn Middle School Renovation",
  "budget": 5200000,
  "planned_duration_days": 450,
  "project_type": "school",
  "start_month": 3,
  "contractor_tier": "A",
  "subcontractor_count": 12,
  "region": "brooklyn"
}
```

## 输出样例 (JSON)

```json
{
  "project_id": "NYC-SCA-2024-001",
  "delay_risk_score": 0.73,
  "risk_level": "HIGH",
  "top_delay_factors": [
    {"factor": "subcontractor_count", "importance": 0.31, "direction": "negative"},
    {"factor": "budget_per_day", "importance": 0.24, "direction": "positive"},
    {"factor": "start_month", "importance": 0.18, "direction": "negative"}
  ],
  "recommended_actions": [
    "增加关键分包商资源",
    "提前采购长周期材料",
    "雨季前完成地基工程"
  ],
  "model_version": "xgboost-v1.0.3",
  "prediction_timestamp": "2026-05-12T10:30:00Z"
}
```

## 失败处理

| 失败场景 | 处理方式 |
|---------|---------|
| API超时 | 降级返回缓存结果 + 告警 |
| 模型推理失败 | 返回"无法评估"状态码 |
| 数据验证失败 | 返回具体字段错误信息 |
| E2E测试失败 | 阻断部署 + 通知 |
| 数据库连接失败 | 切换只读缓存模式 |

## E2E 验收测试用例

### TC-001: 正常预测流程
```python
def test_delay_prediction_flow():
    # 1. 提交有效项目数据
    response = client.post("/predict", json=valid_input)
    assert response.status_code == 200
    assert "delay_risk_score" in response.json()
    assert 0 <= response.json()["delay_risk_score"] <= 1
```

### TC-002: 无效数据拒绝
```python
def test_invalid_data_rejection():
    # 2. 提交无效数据
    invalid_input = {"budget": -100}  # budget不能为负
    response = client.post("/predict", json=invalid_input)
    assert response.status_code == 422  # Validation error
```

### TC-003: E2E完整链路
```python
def test_full_pipeline_e2e():
    # 3. 模拟完整用户流程
    # 登录 → 上传项目 → 获取预测 → 查看报告
    page.goto("/")
    page.click("#upload-project")
    page.upload_file("#file-input", "sample_project.csv")
    page.click("#predict-btn")
    assert page.wait_for_selector("#risk-score")
```

## 部署方式

### 开发环境
```bash
docker-compose up -d  # 启动所有服务
```

### 生产环境
```bash
# GitHub Actions 自动部署流程
# 1. PR合并 → 触发CI
# 2. 运行单元测试 + E2E测试
# 3. 通过 → 自动部署到云端
# 4. 失败 → 阻断 + 通知
```

## 参考GitHub项目

1. **CadenHimes/subcontractor-delay-ai** - AI早期预警系统 (https://github.com/CadenHimes/subcontractor-delay-ai)
2. **EverseDevelopment/e-verse.AIModel.Construction.Schedules** - 进度延迟ML (https://github.com/EverseDevelopment/e-verse.AIModel.Construction.Schedules)
3. **MoAshour93/ConstructionAI** - 建筑GenAI应用 (https://github.com/MoAshour93/ConstructionAI) ⭐24

## 下一步

- [ ] 选择具体MVP范围 (预测 + 预警通知)
- [ ] 确定数据来源 (NYC SCA公开数据)
- [ ] 创建GitHub仓库
- [ ] 实现第一个E2E测试
