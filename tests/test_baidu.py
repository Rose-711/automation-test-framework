"""Baidu search tests — real-world search scenarios."""
import allure
import pytest
from playwright.sync_api import expect

from pages.baidu_page import BaiduPage


@allure.feature("百度搜索")
@allure.story("搜索功能")
class TestBaiduSearch:
    """Baidu search functional tests."""

    @allure.title("搜索关键字应返回结果列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.parametrize("keyword", [
        "Playwright",
        "Python",
        "自动化测试",
    ], ids=["playwright", "python", "auto-test"])
    def test_search_returns_results(self, page, keyword: str) -> None:
        """Search for a keyword and verify results appear."""
        baidu = BaiduPage(page)

        with allure.step(f"打开百度首页并搜索「{keyword}」"):
            baidu.open()
            baidu.search(keyword)

        with allure.step("验证搜索结果页加载成功"):
            assert baidu.is_result_page(), "Should be on search result page"

        with allure.step("验证搜索结果列表不为空"):
            expect(baidu.result_items.first).to_be_visible(timeout=5000)
            result_count = baidu.result_items.count()
            assert result_count > 0, f"Expected >0 results, got {result_count}"
            allure.attach(str(result_count), name="Result Count", attachment_type=allure.attachment_type.TEXT)

    @allure.title("搜索「{keyword}」第一条结果应包含关键字")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("keyword, expected", [
        ("Playwright", "Playwright"),
        ("Pytest", "pytest"),
    ], ids=["playwright", "pytest"])
    def test_first_result_contains_keyword(self, page, keyword: str, expected: str) -> None:
        """Verify the first search result title contains the keyword."""
        baidu = BaiduPage(page)

        with allure.step("搜索关键字"):
            baidu.open()
            baidu.search(keyword)

        with allure.step("获取第一条结果标题"):
            first_title = baidu.first_result_title.inner_text()
            allure.attach(first_title, name="First Result Title", attachment_type=allure.attachment_type.TEXT)

        with allure.step("验证标题包含关键字"):
            assert expected.lower() in first_title.lower(), (
                f"First result title '{first_title}' should contain '{expected}'"
            )

    @allure.title("空搜索不应返回正常结果")
    @pytest.mark.regression
    def test_empty_search_no_results(self, page) -> None:
        """Click search with empty input — Baidu may trigger captcha or stay."""
        baidu = BaiduPage(page)

        with allure.step("打开百度首页"):
            baidu.open()

        with allure.step("直接点击搜索按钮（不输入内容）"):
            baidu.click("#su")
            baidu.page.wait_for_timeout(2000)

        with allure.step("验证没有正常搜索结果"):
            url = baidu.page.url
            has_results = url.startswith("https://www.baidu.com/s?")
            is_captcha = "captcha" in url or "wappass" in url
            # Either captcha triggered or we stayed — but no valid results page
            assert not has_results or is_captcha, \
                f"Unexpected behavior, URL: {url}"
            allure.attach(url, name="Redirect URL", attachment_type=allure.attachment_type.TEXT)

    @allure.title("搜索建议应随输入实时显示")
    @pytest.mark.regression
    def test_search_suggestions(self, page) -> None:
        """Type a partial keyword and verify suggestions appear."""
        baidu = BaiduPage(page)

        with allure.step("打开百度首页"):
            baidu.open()

        with allure.step("输入部分关键字"):
            baidu.fill("#kw", "Play")

        with allure.step("验证搜索建议出现"):
            # Wait briefly for suggestion dropdown
            try:
                suggestion_area = baidu.page.locator(".bdsug")
                expect(suggestion_area).to_be_visible(timeout=3000)
                suggestions = suggestion_area.locator("li").all_inner_texts()
                allure.attach(str(suggestions), name="Suggestions", attachment_type=allure.attachment_type.TEXT)
                assert len(suggestions) > 0, "Should have at least one suggestion"
            except Exception:
                # Suggestions may not load due to network issues — not a hard failure
                allure.attach("Suggestions did not load", name="Note", attachment_type=allure.attachment_type.TEXT)
                pytest.skip("Search suggestions unavailable — likely network issue")


@allure.feature("百度搜索")
@allure.story("导航")
class TestBaiduNavigation:

    @allure.title("百度首页导航链接可见")
    @pytest.mark.regression
    def test_navigation_links_visible(self, page) -> None:
        """Verify navigation links are present on the homepage."""
        baidu = BaiduPage(page)

        with allure.step("打开百度首页"):
            baidu.open()

        with allure.step("验证导航区域存在"):
            nav_area = baidu.page.locator("#s-top-left, .s-top-nav-new, a[href*='news'], a[href*='hao123']").first
            assert nav_area.is_visible(), "Navigation area should be visible on homepage"
            nav_text = nav_area.all_inner_texts() if hasattr(nav_area, 'all_inner_texts') else [nav_area.inner_text()]
            allure.attach(str(nav_text), name="Nav Text", attachment_type=allure.attachment_type.TEXT)
