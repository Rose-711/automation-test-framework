"""Baidu search page object."""
from pages import BasePage
from playwright.sync_api import Page


class BaiduPage(BasePage):
    """Page Object for Baidu (www.baidu.com)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = "https://www.baidu.com"

    # ── Locators ───────────────────────────────────────────
    @property
    def search_input(self):
        return self.page.locator("#kw")

    @property
    def search_button(self):
        return self.page.locator("#su")

    @property
    def result_items(self):
        return self.page.locator(".result")

    @property
    def result_links(self):
        return self.page.locator(".result a")

    @property
    def first_result_title(self):
        return self.page.locator(".result .t a").first

    @property
    def related_searches(self):
        return self.page.locator("#rs")

    @property
    def search_tab_nav(self):
        return self.page.locator("#s_tab")

    # ── Actions ────────────────────────────────────────────
    def open(self) -> None:
        """Navigate to Baidu homepage."""
        self.navigate(self.url)
        self.wait_for_load_state("networkidle")

    def search(self, keyword: str) -> None:
        """Type a keyword and click search."""
        self.fill("#kw", keyword)
        self.wait_for_selector("#su", state="attached")
        self.click("#su")
        self.wait_for_load_state("networkidle")

    def get_result_count_text(self) -> str:
        """Get the result summary text."""
        result_area = self.page.locator(".nums_text")
        if result_area.is_visible():
            return result_area.inner_text()
        return ""

    def is_result_page(self) -> bool:
        """Check if we're on a search result page."""
        return self.page.url.startswith("https://www.baidu.com/s?")

    def get_search_suggestions(self, partial_keyword: str) -> list[str]:
        """Type a partial keyword and get suggestions from dropdown."""
        self.fill("#kw", partial_keyword)
        self.wait_for_selector(".bdsug", state="visible", timeout=3000)
        suggestions = self.page.locator(".bdsug_over")
        return [s.inner_text() for s in suggestions.all() if s.inner_text().strip()]
