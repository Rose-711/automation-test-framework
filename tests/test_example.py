"""Example test suite demonstrating framework features."""
import allure
import pytest
from playwright.sync_api import expect

from pages.example_page import ExamplePage


@allure.feature("Example")
@allure.story("Smoke")
@allure.tag("smoke")
class TestExample:
    """Demo tests against https://example.com."""

    @allure.title("Page heading should display correctly")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_heading_text(self, example_page: ExamplePage) -> None:
        """Verify the main heading on the page."""
        with allure.step("Check heading text"):
            heading = example_page.get_heading_text()
            assert heading == "Example Domain", f"Expected 'Example Domain', got '{heading}'"

    @allure.title("Page should load successfully with correct title")
    @pytest.mark.smoke
    def test_page_title(self, example_page: ExamplePage) -> None:
        """Verify the page title."""
        title = example_page.get_title()
        assert title == "Example Domain", f"Expected 'Example Domain', got '{title}'"

    @allure.title("Page should contain a link")
    def test_has_link(self, example_page: ExamplePage) -> None:
        """Verify there is a link on the page."""
        link = example_page.page.locator("a")
        expect(link).to_be_visible()
        link_text = link.inner_text()
        assert link_text.lower() in ("more information", "learn more")

    @allure.title("URL should be correct")
    def test_url(self, example_page: ExamplePage) -> None:
        """Verify the current URL."""
        url = example_page.get_current_url()
        assert url.rstrip("/") == "https://example.com"

    @allure.title("[Slow] Reload page and verify content persists")
    @pytest.mark.slow
    def test_reload_page(self, example_page: ExamplePage) -> None:
        """Reload the page and check the heading still appears."""
        example_page.reload()
        heading = example_page.get_heading_text()
        assert "Example" in heading


@allure.feature("Example")
@allure.story("Regression")
class TestExampleRegression:

    @allure.title("Paragraph should contain descriptive text")
    @pytest.mark.regression
    def test_paragraph_content(self, example_page: ExamplePage) -> None:
        """Verify the paragraph text is meaningful."""
        paragraph = example_page.get_paragraph_text()
        assert len(paragraph) > 0, "Paragraph should not be empty"
        assert "example" in paragraph.lower()

    @allure.title("Multiple elements should be present on the page")
    @pytest.mark.regression
    def test_multiple_elements(self, example_page: ExamplePage) -> None:
        """Verify multiple elements exist simultaneously."""
        with allure.step("Check heading"):
            assert "Example" in example_page.get_heading_text()
        with allure.step("Check paragraph"):
            assert example_page.is_visible("p")
        with allure.step("Check link"):
            assert example_page.is_visible("a")
