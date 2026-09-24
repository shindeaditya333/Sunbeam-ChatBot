import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraping.base_scraper import BaseScraper


class InternshipScraper(BaseScraper):

    page_name = "Internships"

    def __init__(self):

        edge_options = Options()

        edge_options.add_argument(
            "--headless=new"
        )

        edge_options.add_argument(
            "--window-size=1920,1080"
        )

        self.driver = webdriver.Edge(
            options=edge_options
        )

        self.wait = WebDriverWait(
            self.driver,
            30
        )

        self.driver.implicitly_wait(
            10
        )

    def scrape(self):

        url = (
            "https://sunbeaminfo.in/internship"
        )

        self.driver.get(
            url
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        sections = []

        # -------------------------------------------------
        # PAGE PARAGRAPHS
        # -------------------------------------------------

        for _ in range(4):

            self.driver.execute_script(
                "window.scrollBy(0, 700)"
            )

            time.sleep(0.5)

        paragraphs = (
            self.driver.find_elements(
                By.XPATH,
                "//p"
            )
        )

        page_paragraphs = [

            p.text.strip()

            for p in paragraphs

            if len(
                p.text.strip()
            ) > 30
        ]

        if page_paragraphs:

            sections.append({
                "section_title":
                    "INTERNSHIP OVERVIEW",

                "content":
                    page_paragraphs
            })

        # -------------------------------------------------
        # ACCORDIONS
        # -------------------------------------------------

        accordions = (
            self.driver.find_elements(
                By.CLASS_NAME,
                "panel-heading"
            )
        )

        for accordion in accordions:

            title = accordion.text.strip()

            try:

                content_div = (
                    accordion.find_element(
                        By.XPATH,
                        "following-sibling::div"
                        "[contains(@class,"
                        "'panel-collapse')]"
                    )
                )

            except Exception:

                continue

            self.driver.execute_script(
                """
                arguments[0].style.display = 'block';
                """,
                content_div
            )

            text_blocks = []

            elements = (
                content_div.find_elements(
                    By.XPATH,
                    ".//p | .//li"
                )
            )

            for element in elements:

                text = element.text.strip()

                if text:

                    text_blocks.append(
                        text
                    )

            # -------------------------------------------------
            # TABLES
            # -------------------------------------------------

            tables = []

            page_tables = (
                content_div.find_elements(
                    By.XPATH,
                    ".//table"
                )
            )

            for table in page_tables:

                rows_data = []

                rows = (
                    table.find_elements(
                        By.TAG_NAME,
                        "tr"
                    )
                )

                for row in rows:

                    cols = (
                        row.find_elements(
                            By.XPATH,
                            ".//th | .//td"
                        )
                    )

                    row_data = [
                        col.text.strip()
                        for col in cols
                        if col.text.strip()
                    ]

                    if row_data:

                        rows_data.append(
                            row_data
                        )

                if rows_data:

                    tables.append(
                        rows_data
                    )

            content = list(
                text_blocks
            )

            for table in tables:

                for row in table:

                    content.append(
                        " | ".join(row)
                    )

            if content:

                sections.append({
                    "section_title":
                        title,

                    "content":
                        content
                })

        return {
            "url": url,
            "title": self.driver.title.strip()
            or "Sunbeam Internships",
            "sections": sections
        }

    def close(self):

        try:
            self.driver.quit()
        except Exception:
            pass