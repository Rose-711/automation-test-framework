"""UI interaction tests — using a local HTML test page.

Runs against a self-contained local page (no network required).
"""
import allure
import pytest
from playwright.sync_api import expect

from pages import BasePage


LOCAL_PAGE = "file:///D:/VibeCoding/automation-test-framework/testdata/test_page.html"


class LocalTestPage(BasePage):
    """Page Object for the local test page."""

    def __init__(self, page):
        super().__init__(page)
        self.url = LOCAL_PAGE

    def open(self) -> None:
        self.navigate(self.url)
        self.wait_for_load_state("networkidle")

    # ── Checkboxes ──
    @property
    def hobby_checkboxes(self):
        return self.page.locator("input[name='hobby']")

    def get_checked_count(self) -> int:
        return int(self.page.locator("#checked-count").inner_text())

    def check_all_hobbies(self) -> None:
        for i in range(self.hobby_checkboxes.count()):
            if not self.hobby_checkboxes.nth(i).is_checked():
                self.hobby_checkboxes.nth(i).check()

    def uncheck_all_hobbies(self) -> None:
        for i in range(self.hobby_checkboxes.count()):
            if self.hobby_checkboxes.nth(i).is_checked():
                self.hobby_checkboxes.nth(i).uncheck()

    def get_hobby_states(self) -> list[bool]:
        return [self.hobby_checkboxes.nth(i).is_checked() for i in range(self.hobby_checkboxes.count())]

    # ── Dropdown ──
    def select_city(self, value: str) -> None:
        self.select_option("#city-select", value)

    def get_selected_city(self) -> str:
        return self.page.locator("#selected-city").inner_text()

    # ── Form ──
    def fill_form(self, username: str, email: str, password: str, confirm: str) -> None:
        self.fill("#username", username)
        self.fill("#email", email)
        self.fill("#password", password)
        self.fill("#confirm-password", confirm)

    def submit_form(self) -> None:
        self.click("button[type='submit']")

    def get_form_result(self) -> str:
        return self.page.locator("#form-result").inner_text()

    # ── Dynamic content ──
    def click_load_content(self) -> None:
        self.click("#load-content")

    def get_dynamic_content(self) -> str:
        return self.page.locator("#dynamic-content").inner_text()

    def wait_for_dynamic_content(self, timeout: int = 5000) -> str:
        content = self.page.locator("#dynamic-content")
        expect(content).to_be_visible(timeout=timeout)
        # Wait for the async content to arrive
        self.page.wait_for_function(
            "document.getElementById('dynamic-content').innerText.includes('✅')",
            timeout=timeout,
        )
        return content.inner_text()

    # ── Search ──
    def search(self, keyword: str) -> None:
        self.fill("#search-input", keyword)
        self.click("#search-btn")

    def get_search_results(self) -> list[str]:
        items = self.page.locator(".result-item")
        return [items.nth(i).inner_text() for i in range(items.count())]


# ── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def local_page(page) -> LocalTestPage:
    p = LocalTestPage(page)
    p.open()
    return p


# ── Tests ────────────────────────────────────────────────────────────────────

@allure.feature("UI交互")
@allure.story("复选框")
class TestCheckboxes:

    @allure.title("页面应包含4个爱好复选框")
    @pytest.mark.smoke
    def test_checkbox_count(self, local_page: LocalTestPage) -> None:
        assert local_page.hobby_checkboxes.count() == 4

    @allure.title("初始状态：音乐和旅行默认选中")
    @pytest.mark.smoke
    def test_default_checked(self, local_page: LocalTestPage) -> None:
        states = local_page.get_hobby_states()
        assert states == [False, True, False, True], f"Unexpected states: {states}"
        assert local_page.get_checked_count() == 2

    @allure.title("全选和取消全选功能")
    @pytest.mark.regression
    def test_check_uncheck_all(self, local_page: LocalTestPage) -> None:
        with allure.step("点击全选"):
            local_page.check_all_hobbies()
            assert all(local_page.get_hobby_states()), "All should be checked"
            assert local_page.get_checked_count() == 4

        with allure.step("点击取消全选"):
            local_page.uncheck_all_hobbies()
            assert not any(local_page.get_hobby_states()), "All should be unchecked"
            assert local_page.get_checked_count() == 0

    @allure.title("单个复选框切换")
    @pytest.mark.regression
    def test_toggle_single_checkbox(self, local_page: LocalTestPage) -> None:
        with allure.step("取消选中「音乐」"):
            local_page.hobby_checkboxes.nth(1).uncheck()
            assert local_page.get_checked_count() == 1

        with allure.step("选中「阅读」"):
            local_page.hobby_checkboxes.nth(0).check()
            assert local_page.get_checked_count() == 2


@allure.feature("UI交互")
@allure.story("下拉菜单")
class TestDropdown:

    @allure.title("选择「上海」应显示正确")
    @pytest.mark.smoke
    def test_select_shanghai(self, local_page: LocalTestPage) -> None:
        local_page.select_city("shanghai")
        assert local_page.get_selected_city() == "上海"

    @allure.title("切换多个选项应正确更新显示")
    @pytest.mark.regression
    def test_switch_cities(self, local_page: LocalTestPage) -> None:
        with allure.step("选择北京"):
            local_page.select_city("beijing")
            assert local_page.get_selected_city() == "北京"

        with allure.step("切换到深圳"):
            local_page.select_city("shenzhen")
            assert local_page.get_selected_city() == "深圳"

    @allure.title("未选择时应显示占位文本")
    @pytest.mark.regression
    def test_default_no_selection(self, local_page: LocalTestPage) -> None:
        assert local_page.get_selected_city() == "未选择"


@allure.feature("UI交互")
@allure.story("表单")
class TestForm:

    @allure.title("空用户名提交应提示错误")
    @pytest.mark.smoke
    def test_empty_username(self, local_page: LocalTestPage) -> None:
        local_page.fill_form("", "a@b.com", "123", "123")
        local_page.submit_form()
        assert local_page.get_form_result() == "请输入用户名"

    @allure.title("两次密码不一致应报错")
    @pytest.mark.smoke
    def test_password_mismatch(self, local_page: LocalTestPage) -> None:
        local_page.fill_form("testuser", "a@b.com", "123456", "654321")
        local_page.submit_form()
        assert local_page.get_form_result() == "两次密码不一致"

    @allure.title("正确填写表单应提交成功")
    @pytest.mark.regression
    def test_successful_submit(self, local_page: LocalTestPage) -> None:
        local_page.fill_form("testuser", "test@example.com", "pass123", "pass123")
        local_page.submit_form()
        assert local_page.get_form_result() == "提交成功！"


@allure.feature("UI交互")
@allure.story("动态内容")
class TestDynamicContent:

    @allure.title("点击「加载内容」后应显示动态加载的文本")
    @pytest.mark.regression
    def test_dynamic_loading(self, local_page: LocalTestPage) -> None:
        with allure.step("点击加载按钮"):
            local_page.click_load_content()

        with allure.step("等待动态内容加载完成"):
            content = local_page.wait_for_dynamic_content()

        with allure.step("验证内容包含成功标记"):
            assert "✅" in content
            assert "动态内容加载完成" in content
            allure.attach(content, name="Dynamic Content", attachment_type=allure.attachment_type.TEXT)

    @allure.title("初始状态动态内容区域应隐藏")
    @pytest.mark.smoke
    def test_content_hidden_initially(self, local_page: LocalTestPage) -> None:
        content = local_page.page.locator("#dynamic-content")
        assert content.is_hidden(), "Content should be hidden before clicking"


@allure.feature("UI交互")
@allure.story("搜索")
class TestLocalSearch:

    @allure.title("搜索「Playwright」应返回相关结果")
    @pytest.mark.regression
    def test_search_found(self, local_page: LocalTestPage) -> None:
        local_page.search("Playwright")
        results = local_page.get_search_results()
        assert len(results) > 0, "Should return results"
        assert any("Playwright" in r for r in results)
        allure.attach("\n".join(results), name="Search Results", attachment_type=allure.attachment_type.TEXT)

    @allure.title("空搜索应提示输入关键字")
    @pytest.mark.smoke
    def test_empty_search(self, local_page: LocalTestPage) -> None:
        local_page.search("")
        error = local_page.page.locator("p[style*='color:red']")
        assert error.is_visible()
        assert "请输入搜索关键字" in error.inner_text()

    @allure.title("搜索不存在的关键字应返回「未找到结果」")
    @pytest.mark.regression
    def test_search_not_found(self, local_page: LocalTestPage) -> None:
        local_page.search("ZZZZNotExist")
        assert local_page.page.locator("text=未找到结果").is_visible()
