"""Page Objects for https://the-internet.herokuapp.com/ practice site."""
from pages import BasePage
from playwright.sync_api import Page


class InternetBase(BasePage):
    """Base for the-internet test pages."""

    base_url = "https://the-internet.herokuapp.com"

    def __init__(self, page: Page):
        super().__init__(page)


class CheckboxesPage(InternetBase):
    """Page Object for /checkboxes."""

    path = "/checkboxes"

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.base_url}{self.path}"

    @property
    def checkboxes(self):
        return self.page.locator("input[type='checkbox']")

    @property
    def heading(self):
        return self.page.locator("h3")

    def open(self) -> None:
        self.navigate(self.url)
        self.wait_for_load_state("networkidle")

    def check_all(self) -> None:
        """Check all unchecked checkboxes."""
        for i in range(self.checkboxes.count()):
            if not self.checkboxes.nth(i).is_checked():
                self.checkboxes.nth(i).check()

    def uncheck_all(self) -> None:
        """Uncheck all checked checkboxes."""
        for i in range(self.checkboxes.count()):
            if self.checkboxes.nth(i).is_checked():
                self.checkboxes.nth(i).uncheck()

    def get_checkbox_states(self) -> list[bool]:
        """Return list of checked states for all checkboxes."""
        return [self.checkboxes.nth(i).is_checked() for i in range(self.checkboxes.count())]


class DropdownPage(InternetBase):
    """Page Object for /dropdown."""

    path = "/dropdown"

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.base_url}{self.path}"

    @property
    def dropdown(self):
        return self.page.locator("#dropdown")

    @property
    def heading(self):
        return self.page.locator("h3")

    def open(self) -> None:
        self.navigate(self.url)
        self.wait_for_load_state("networkidle")

    def select_by_value(self, value: str) -> None:
        """Select dropdown option by value attribute."""
        self.select_option("#dropdown", value)

    def select_by_label(self, label: str) -> None:
        """Select dropdown option by visible text."""
        self.select_option_by_label("#dropdown", label)

    def get_selected_text(self) -> str:
        """Get the text of the currently selected option."""
        return self.dropdown.locator("option:checked").inner_text()


class DynamicLoadingPage(InternetBase):
    """Page Object for /dynamic_loading."""

    path = "/dynamic_loading"

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.base_url}{self.path}"

    def open_example(self, example: int = 1) -> None:
        """Open example 1 or 2."""
        self.navigate(f"{self.base_url}/dynamic_loading/{example}")
        self.wait_for_load_state("networkidle")

    @property
    def start_button(self):
        return self.page.locator("#start button")

    @property
    def finish_text(self):
        return self.page.locator("#finish")

    def click_start_and_wait(self, timeout: int = 10000) -> str:
        """Click Start, wait for loading to finish, return the result text."""
        self.start_button.click()
        self.finish_text.wait_for(state="visible", timeout=timeout)
        return self.finish_text.inner_text()
