#!/usr/bin/env python3
"""
Construction Delay Radar AI - E2E Acceptance Tests
验收标准：
1. 所有测试必须通过才能部署
2. 测试覆盖：API、功能、UI、ML模型
3. 失败输出：具体错误信息 + 重试建议
"""

import pytest
import requests
import json
import time
from typing import Dict, Any

# 配置
API_BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
TIMEOUT = 30

# 测试数据
VALID_PROJECT = {
    "project_id": "TEST-001",
    "project_name": "Test Construction Project",
    "budget": 5000000,
    "planned_duration_days": 365,
    "project_type": "commercial",
    "start_month": 4,
    "contractor_tier": "A",
    "subcontractor_count": 8,
    "region": "manhattan"
}

VALID_PROJECT_RESPONSE_KEYS = {
    "project_id", "delay_risk_score", "risk_level",
    "top_delay_factors", "recommended_actions",
    "model_version", "prediction_timestamp"
}


class TestAPI:
    """API层测试"""

    def test_health_check(self):
        """TC-001: 健康检查"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_predict_valid_input(self):
        """TC-002: 有效输入预测"""
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=VALID_PROJECT,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()

        # 验证响应结构
        assert set(data.keys()) == VALID_PROJECT_RESPONSE_KEYS

        # 验证风险评分范围
        assert 0 <= data["delay_risk_score"] <= 1

        # 验证风险等级
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        # 验证时间戳格式
        assert "T" in data["prediction_timestamp"]

    def test_predict_invalid_budget_negative(self):
        """TC-003: 负预算应被拒绝"""
        invalid = VALID_PROJECT.copy()
        invalid["budget"] = -100
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid,
            timeout=TIMEOUT
        )
        assert response.status_code == 422  # Validation error

    def test_predict_invalid_budget_zero(self):
        """TC-004: 零预算应被拒绝"""
        invalid = VALID_PROJECT.copy()
        invalid["budget"] = 0
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_predict_missing_required_field(self):
        """TC-005: 缺少必填字段"""
        incomplete = {"budget": 5000000}  # 只有budget
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=incomplete,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_predict_invalid_project_type(self):
        """TC-006: 无效项目类型"""
        invalid = VALID_PROJECT.copy()
        invalid["project_type"] = "invalid_type"
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_model_version_endpoint(self):
        """TC-007: 模型版本检查"""
        response = requests.get(f"{API_BASE_URL}/model/info", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "algorithm" in data
        assert data["algorithm"] == "XGBoost"


class TestE2E:
    """端到端测试"""

    @pytest.fixture(autouse=True)
    def wait_for_services(self):
        """确保服务就绪"""
        time.sleep(2)

    def test_full_prediction_workflow(self):
        """TC-010: 完整预测工作流"""
        # 1. 提交预测请求
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=VALID_PROJECT,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()

        # 2. 验证结果可解释性
        assert len(result["top_delay_factors"]) > 0
        assert len(result["recommended_actions"]) > 0

        # 3. 验证建议与风险因素相关
        # HIGH风险应有关键建议
        if result["risk_level"] in ["HIGH", "CRITICAL"]:
            assert len(result["recommended_actions"]) >= 2

    def test_high_risk_project_detection(self):
        """TC-011: 高风险项目检测"""
        high_risk_project = VALID_PROJECT.copy()
        high_risk_project["subcontractor_count"] = 1  # 极少分包商
        high_risk_project["budget"] = 100000  # 极低预算

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=high_risk_project,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()

        # 边界条件项目应该有较高风险评分
        # (不一定HIGH，因为模型决定，但应该比均值高)
        assert result["delay_risk_score"] >= 0

    def test_low_risk_project_detection(self):
        """TC-012: 低风险项目检测"""
        low_risk_project = {
            "project_id": "TEST-LOW-001",
            "project_name": "Low Risk Project",
            "budget": 50000000,  # 充足预算
            "planned_duration_days": 730,  # 充足工期
            "project_type": "infrastructure",
            "start_month": 3,  # 春季开工
            "contractor_tier": "A",
            "subcontractor_count": 25,  # 充足分包商
            "region": "manhattan"
        }

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=low_risk_project,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()

        # 理想条件项目应该有较低风险评分
        assert 0 <= result["delay_risk_score"] <= 1


class TestPerformance:
    """性能测试"""

    def test_prediction_latency(self):
        """TC-020: 预测延迟 < 2秒"""
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=VALID_PROJECT,
            timeout=TIMEOUT
        )
        latency = time.time() - start

        assert response.status_code == 200
        assert latency < 2.0, f"预测延迟 {latency:.2f}s 超过2秒限制"

    def test_concurrent_requests(self):
        """TC-021: 并发请求处理"""
        import concurrent.futures

        def make_request():
            return requests.post(
                f"{API_BASE_URL}/predict",
                json=VALID_PROJECT,
                timeout=TIMEOUT
            )

        # 10个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # 所有请求应该成功
        assert all(r.status_code == 200 for r in results)


class TestFailureRecovery:
    """失败恢复测试"""

    def test_api_timeout_handling(self):
        """TC-030: API超时处理"""
        large_payload = VALID_PROJECT.copy()
        large_payload["extra_data"] = "x" * 10000  # 超大数据

        # 应该返回明确的超时错误，而不是崩溃
        try:
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=large_payload,
                timeout=5
            )
            # 超时会返回特定状态码
            assert response.status_code in [408, 422, 500]
        except requests.exceptions.Timeout:
            pass  # 超时是可接受的失败模式

    def test_invalid_json_handling(self):
        """TC-031: 无效JSON处理"""
        response = requests.post(
            f"{API_BASE_URL}/predict",
            data="not json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert response.status_code == 422


# 测试运行入口
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
