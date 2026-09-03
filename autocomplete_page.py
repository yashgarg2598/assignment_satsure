"""Page Object for the Autocomplete form.

Locators only — assertions live in the tests, and Playwright's own auto-waiting locators and
keyboard API do all the work, so there are no custom waits or helpers here.
"""
import re

from tests.ui.config import settings


class AutocompletePage:
    def __init__(self, page):
        self.page = page
        self.label = page.get_by_text("Enter a value:")
        self.input = page.locator("#input-field")
        self.suggestions = page.locator("ul.suggestions li")
        self.next_button = page.locator("#next-button")
        self.error_message = page.locator("span.error-message")
        self.success_container = page.locator("div.success-container")

    def open(self, match_anywhere: bool = False):
        """Load the form. match_anywhere selects the FR-03 configuration."""
        query = "?match=anywhere" if match_anywhere else ""
        self.page.goto(f"{settings.FORM_PATH}{query}")
        return self

    def type_value(self, value: str):
        self.input.fill("")
        self.input.type(value)

    def visible_suggestions(self) -> list[str]:
        return self.suggestions.filter(visible=True).all_text_contents()

    def select_suggestion(self, text: str):
        self.suggestions.filter(has_text=re.compile(f"^{re.escape(text)}$")).click()

    def submit(self):
        self.next_button.click()

    def press(self, key: str):
        self.page.keyboard.press(key)

    def focused_id(self) -> str:
        return self.page.evaluate("document.activeElement.id")
