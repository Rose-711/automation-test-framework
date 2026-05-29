"""Example: test parametrization and Allure reporting."""
import allure
import pytest
from playwright.sync_api import Page


@allure.feature("Search")
@allure.story("Basic search")
class TestSearch:
    """Demonstrates parametrized tests and Allure reporting."""

    @allure.title("Navigate to {base_url} with query: {query}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["Playwright", "Pytest", "Allure"], ids=["pw", "pt", "al"])
    def test_search_engine(self, page: Page, base_url: str, query: str) -> None:
        """Navigate to the base URL and verify the page loads."""
        with allure.step(f"Navigate to {base_url}"):
            page.goto(base_url, wait_until="load")

        with allure.step("Verify page loaded"):
            assert page.title() is not None
            allure.attach(
                page.title() or "Untitled",
                name="Page Title",
                attachment_type=allure.attachment_type.TEXT,
            )
