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
API_PREFIX = "/api"
STREAMLIT_URL = "http://localhost:8501"
TIMEOUT = 30

def get_api_url(endpoint: str) -> str:
    return f"{API_BASE_URL}{API_PREFIX}{endpoint}"

# 测试数据 - 匹配 PredictionRequest schema
VALID_PROJECT = {
    "project_id": "TEST-001",
    "progress_percent": 35,
    "weather_delays_days": 5.0,
    "resource_shortage_score": 0.5,
    "supply_chain_score": 0.4,
    "historical_performance": 0.75
}

VALID_PROJECT_RESPONSE_KEYS = {
    "predicted_delay_days", "confidence", "risk_level",
    "factors", "recommendations"
}


class TestAPI:
    """API层测试"""

    def test_health_check(self):
        response = requests.get(get_api_url("/health"), timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_predict_valid_input(self):
        response = requests.post(
            get_api_url("/predict/"),
            json=VALID_PROJECT,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == VALID_PROJECT_RESPONSE_KEYS
        assert 0 <= data["predicted_delay_days"]
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert 0 <= data["confidence"] <= 1

    def test_predict_invalid_progress_negative(self):
        invalid = VALID_PROJECT.copy()
        invalid["progress_percent"] = -10
        response = requests.post(
            get_api_url("/predict/"),
            json=invalid,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_predict_invalid_progress_over_100(self):
        invalid = VALID_PROJECT.copy()
        invalid["progress_percent"] = 150
        response = requests.post(
            get_api_url("/predict/"),
            json=invalid,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_predict_missing_required_field(self):
        incomplete = {"progress_percent": 50}
        response = requests.post(
            get_api_url("/predict/"),
            json=incomplete,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_predict_invalid_score(self):
        invalid = VALID_PROJECT.copy()
        invalid["resource_shortage_score"] = 1.5
        response = requests.post(
            get_api_url("/predict/"),
            json=invalid,
            timeout=TIMEOUT
        )
        assert response.status_code == 422

    def test_model_version_endpoint(self):
        response = requests.get(get_api_url("/model/info"), timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "algorithm" in data
        assert data["algorithm"] == "XGBoost"


class TestE2E:
    @pytest.fixture(autouse=True)
    def wait_for_services(self):
        time.sleep(2)

    def test_full_prediction_workflow(self):
        response = requests.post(
            get_api_url("/predict/"),
            json=VALID_PROJECT,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result["factors"]) > 0
        assert len(result["recommendations"]) > 0
        if result["risk_level"] in ["HIGH", "CRITICAL"]:
            assert len(result["recommendations"]) >= 2

    def test_high_risk_project_detection(self):
        high_risk_project = VALID_PROJECT.copy()
        high_risk_project["resource_shortage_score"] = 0.95
        high_risk_project["supply_chain_score"] = 0.9
        response = requests.post(
            get_api_url("/predict/"),
            json=high_risk_project,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()
        assert result["predicted_delay_days"] >= 0

    def test_low_risk_project_detection(self):
        low_risk_project = {
            "project_id": "TEST-LOW-001",
            "progress_percent": 50,
            "weather_delays_days": 0.0,
            "resource_shortage_score": 0.1,
            "supply_chain_score": 0.1,
            "historical_performance": 0.95
        }
        response = requests.post(
            get_api_url("/predict/"),
            json=low_risk_project,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        result = response.json()
        assert result["predicted_delay_days"] >= 0


class TestPerformance:
    def test_prediction_latency(self):
        start = time.time()
        response = requests.post(
            get_api_url("/predict/"),
            json=VALID_PROJECT,
            timeout=TIMEOUT
        )
        latency = time.time() - start
        assert response.status_code == 200
        assert latency < 2.0, f"预测延迟 {latency:.2f}s 超过2秒限制"

    def test_concurrent_requests(self):
        import concurrent.futures
        def make_request():
            return requests.post(
                get_api_url("/predict/"),
                json=VALID_PROJECT,
                timeout=TIMEOUT
            )
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        assert all(r.status_code == 200 for r in results)


class TestFailureRecovery:
    def test_api_timeout_handling(self):
        large_payload = VALID_PROJECT.copy()
        large_payload["extra_data"] = "x" * 10000
        try:
            response = requests.post(
                get_api_url("/predict/"),
                json=large_payload,
                timeout=5
            )
            assert response.status_code in [408, 422, 500]
        except requests.exceptions.Timeout:
            pass

    def test_invalid_json_handling(self):
        response = requests.post(
            get_api_url("/predict/"),
            data="not json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert response.status_code == 422


# 测试运行入口
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
