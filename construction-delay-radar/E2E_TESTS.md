# E2E验收测试 - Construction Delay Radar

## 验收标准

### 必须通过的测试

| 测试ID | 测试内容 | 验收标准 |
|--------|---------|---------|
| TC-E2E-001 | 健康检查 | GET /api/health 返回 200 |
| TC-E2E-002 | 创建项目 | POST /api/projects/ 返回 201 |
| TC-E2E-003 | 延迟预测 | POST /api/predict/ 返回 200 |
| TC-E2E-004 | 无效数据拒绝 | 负预算返回 422 |
| TC-E2E-005 | 响应时间 | 预测API响应 < 2秒 |

## 运行方式

```bash
# 启动服务
docker-compose up -d

# 运行E2E测试
pytest e2e_tests.py -v

# 查看测试覆盖
pytest e2e_tests.py --collect-only
```

## 测试用例

### TC-E2E-001: 健康检查
```python
def test_e2e_health():
    response = requests.get("http://localhost:8000/api/health")
    assert response.status_code == 200
```

### TC-E2E-002: 项目创建
```python
def test_e2e_create_project():
    response = requests.post("http://localhost:8000/api/projects/", json={
        "name": "Test Project",
        "location": "Beijing",
        "start_date": "2026-07-01",
        "duration_days": 120
    })
    assert response.status_code == 201
```

### TC-E2E-003: 延迟预测
```python
def test_e2e_predict():
    response = requests.post("http://localhost:8000/api/predict/", json={
        "project_id": "proj_001",
        "progress_percent": 35,
        "weather_delays_days": 5,
        "resource_shortage_score": 0.6,
        "supply_chain_score": 0.4,
        "historical_performance": 0.78
    })
    assert response.status_code == 200
    assert "predicted_delay_days" in response.json()
```

### TC-E2E-004: 无效数据拒绝
```python
def test_e2e_invalid_data():
    response = requests.post("http://localhost:8000/api/predict/", json={
        "project_id": "proj_bad",
        "progress_percent": -10,  # 无效值
        "weather_delays_days": 5,
        "resource_shortage_score": 0.6,
        "supply_chain_score": 0.4,
        "historical_performance": 0.78
    })
    assert response.status_code == 422
```

### TC-E2E-005: 响应时间
```python
def test_e2e_latency():
    start = time.time()
    response = requests.post("http://localhost:8000/api/predict/", json={...})
    latency = time.time() - start
    assert latency < 2.0
```

## 失败处理

| 场景 | 处理 |
|------|------|
| API超时 | 重试3次，间隔2秒 |
| 连接失败 | 等待5秒后重试 |
| 测试失败 | 阻断CI/CD流程 |
| 性能不达标 | 记录到监控面板 |

## 部署验收

1. 代码合并到main分支
2. GitHub Actions自动运行E2E测试
3. 测试通过 → 自动部署到staging
4. staging验证通过 → 手动确认生产部署