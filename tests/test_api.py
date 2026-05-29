"""API tests — using the JSONPlaceholder public API.

Target: https://jsonplaceholder.typicode.com/ (free, no auth, accessible)
"""
import allure
import pytest
import requests


# ── Helper ────────────────────────────────────────────────────────────────────

BASE_API = "https://jsonplaceholder.typicode.com"
TIMEOUT = 15


@allure.feature("API测试")
@allure.story("GET 请求")
class TestGetAPI:
    """Test GET endpoints."""

    @allure.title("获取所有文章列表")
    @pytest.mark.smoke
    def test_get_all_posts(self) -> None:
        """GET /posts should return 100 posts."""
        with allure.step("发送 GET /posts"):
            resp = requests.get(f"{BASE_API}/posts", timeout=TIMEOUT)

        with allure.step("验证状态码 200"):
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

        data = resp.json()
        with allure.step("验证返回 100 篇文章"):
            assert len(data) == 100, f"Expected 100 posts, got {len(data)}"

        with allure.step("验证数据结构"):
            first = data[0]
            assert "userId" in first
            assert "id" in first
            assert "title" in first
            assert "body" in first
            allure.attach(str(first), name="First Post", attachment_type=allure.attachment_type.TEXT)

    @allure.title("通过ID获取单篇文章")
    @pytest.mark.regression
    @pytest.mark.parametrize("post_id, expected_title_prefix", [
        (1, "sunt"),
        (2, "qui"),
    ], ids=["post-1", "post-2"])
    def test_get_post_by_id(self, post_id: int, expected_title_prefix: str) -> None:
        """GET /posts/:id should return the correct post."""
        with allure.step(f"获取第 {post_id} 篇文章"):
            resp = requests.get(f"{BASE_API}/posts/{post_id}", timeout=TIMEOUT)

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == post_id
        assert data["title"].startswith(expected_title_prefix), \
            f"Title '{data['title']}' should start with '{expected_title_prefix}'"

    @allure.title("获取不存在的文章应返回 404")
    @pytest.mark.regression
    def test_get_nonexistent_post(self) -> None:
        """GET /posts/99999 should return 404."""
        resp = requests.get(f"{BASE_API}/posts/99999", timeout=TIMEOUT)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    @allure.title("获取文章的评论列表")
    @pytest.mark.regression
    def test_get_post_comments(self) -> None:
        """GET /posts/1/comments should return comments."""
        resp = requests.get(f"{BASE_API}/posts/1/comments", timeout=TIMEOUT)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Should have comments"
        assert "email" in data[0], "Comment should have email field"
        allure.attach(str(len(data)), name="Comment Count", attachment_type=allure.attachment_type.TEXT)


@allure.feature("API测试")
@allure.story("POST 请求")
class TestPostAPI:
    """Test POST endpoints."""

    @allure.title("创建新文章")
    @pytest.mark.smoke
    def test_create_post(self) -> None:
        """POST /posts should create and return the new post."""
        payload = {
            "title": "foo",
            "body": "bar",
            "userId": 1,
        }

        with allure.step("发送 POST 请求创建文章"):
            resp = requests.post(f"{BASE_API}/posts", json=payload, timeout=TIMEOUT)

        with allure.step("验证状态码 201"):
            assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"

        data = resp.json()
        with allure.step("验证返回的数据包含创建的字段"):
            assert data["title"] == "foo"
            assert data["body"] == "bar"
            assert data["userId"] == 1
            assert "id" in data
            allure.attach(str(data), name="Created Post", attachment_type=allure.attachment_type.TEXT)


@allure.feature("API测试")
@allure.story("PUT 请求")
class TestPutAPI:

    @allure.title("更新整篇文章")
    @pytest.mark.regression
    def test_update_post(self) -> None:
        """PUT /posts/1 should fully update the post."""
        payload = {
            "id": 1,
            "title": "updated title",
            "body": "updated body",
            "userId": 1,
        }

        resp = requests.put(f"{BASE_API}/posts/1", json=payload, timeout=TIMEOUT)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "updated title"
        assert data["body"] == "updated body"
        allure.attach(str(data), name="Updated Post", attachment_type=allure.attachment_type.TEXT)


@allure.feature("API测试")
@allure.story("DELETE 请求")
class TestDeleteAPI:

    @allure.title("删除文章")
    @pytest.mark.regression
    def test_delete_post(self) -> None:
        """DELETE /posts/1 should return 200."""
        resp = requests.delete(f"{BASE_API}/posts/1", timeout=TIMEOUT)
        assert resp.status_code in (200, 204), f"Expected 200/204, got {resp.status_code}"
        allure.attach(str(resp.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)
