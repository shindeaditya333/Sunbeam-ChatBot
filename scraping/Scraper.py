import json
import time

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Courses_scraper:

    def __init__(self):

        options = Options()

        options.add_argument(
            "--headless=new"
        )

        options.add_argument(
            "--window-size=1920,1080"
        )

        self.driver = webdriver.Edge(
            options=options
        )

        self.wait = WebDriverWait(
            self.driver,
            20
        )

        self.visited = set()

    def scrape(
        self,
        url
    ):

        if url in self.visited:
            return None

        self.visited.add(url)

        sections = []

        self.driver.get(
            url
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        # =================================================
        # ABOUT US
        # =================================================

        if "about-us" in url.lower():

            about_section = {
                "section_title": "ABOUT SUNBEAM",
                "content": []
            }

            about_paragraphs = (
                self.driver.find_elements(
                    By.XPATH,
                    "//div[@id='about_us_page']"
                    "//div[contains(@class,'main_info')]//p"
                )
            )

            for p in about_paragraphs:

                text = p.text.strip()

                if len(text) > 30:

                    about_section[
                        "content"
                    ].append(text)

            if about_section["content"]:

                sections.append(
                    about_section
                )

        # =================================================
        # CONTACT US
        # =================================================

        if "contact-us" in url.lower():

            contact_section = {
                "section_title":
                    "CONTACT DETAILS",
                "content": []
            }

            seen = set()

            centre_blocks = (
                self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class,"
                    "'contact_page_info')]"
                    "//div[contains(@class,'wow')]"
                )
            )

            for block in centre_blocks:

                texts = block.find_elements(
                    By.XPATH,
                    ".//p | .//a"
                )

                for element in texts:

                    text = element.text.strip()

                    if not text:
                        continue

                    if text in seen:
                        continue

                    seen.add(text)

                    clean = (
                        text
                        .replace(" ", "")
                        .replace("+", "")
                        .replace("-", "")
                    )

                    if (
                        clean.isdigit()
                        and len(clean) >= 8
                    ):

                        contact_section[
                            "content"
                        ].append(
                            f"Phone: {text}"
                        )

                    elif "@" in text:

                        contact_section[
                            "content"
                        ].append(
                            f"Email: {text}"
                        )

                    else:

                        contact_section[
                            "content"
                        ].append(
                            f"Address: {text}"
                        )

            if contact_section["content"]:

                sections.append(
                    contact_section
                )

        # =================================================
        # MODULAR COURSE HOME
        # =================================================

        if "modular-courses-home" in url:

            hrefs = [

                a.get_attribute(
                    "href"
                )

                for a in self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class,"
                    "'c_cat_box')]"
                    "//a[contains(@class,"
                    "'c_cat_more_btn')]"
                )

                if a.get_attribute("href")

                and "modular-courses.php?mdid="
                not in a.get_attribute("href")
            ]

            nested_data = []

            for href in hrefs:

                result = self.scrape(
                    urljoin(
                        url,
                        href
                    )
                )

                if not result:
                    continue

                if isinstance(
                    result,
                    list
                ):

                    nested_data.extend(
                        result
                    )

                else:

                    nested_data.append(
                        result
                    )

            return nested_data

        # =================================================
        # TITLE
        # =================================================

        title = self.driver.title.strip()

        try:

            h1 = self.driver.find_element(
                By.TAG_NAME,
                "h1"
            ).text.strip()

        except Exception:

            h1 = ""

        try:

            h4 = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,"
                "'course-title')]//h4"
            ).text.strip()

        except Exception:

            h4 = ""

        if (
            not title
            or title.upper()
            in (
                "COURSES",
                "SUNBEAM",
                "TRAINING"
            )
        ):

            if h1:
                title = h1

            elif h4:
                title = h4

            else:
                title = "(No title found)"

        page_title = title

        # =================================================
        # OVERVIEW
        # =================================================

        static_section = {
            "section_title": "OVERVIEW",
            "content": []
        }

        page_header = ""

        try:

            page_header = (
                self.driver.find_element(
                    By.XPATH,
                    "//h3[contains(@class,"
                    "'inner_page_head')]"
                ).text.strip()
            )

        except Exception:
            pass

        if not page_header:

            try:

                page_header = (
                    self.driver.find_element(
                        By.TAG_NAME,
                        "h1"
                    ).text.strip()
                )

            except Exception:
                pass

        if not page_header:

            try:

                page_header = (
                    self.driver.find_element(
                        By.XPATH,
                        "//div[contains(@class,"
                        "'course-title')]//h4"
                    ).text.strip()
                )

            except Exception:
                pass

        if page_header:

            static_section[
                "content"
            ].append(
                page_header
            )

        static_blocks = (
            self.driver.find_elements(
                By.XPATH,
                """
                //div[contains(@class,'course_info')]//h3
                |
                //div[contains(@class,'course_info')]//p
                """
            )
        )

        for element in static_blocks:

            text = element.text.strip()

            if text:

                static_section[
                    "content"
                ].append(text)

        if static_section["content"]:

            sections.append(
                static_section
            )

        # =================================================
        # ACCORDIONS
        # =================================================

        accordion_buttons = (
            self.driver.find_elements(
                By.XPATH,
                "//a[@data-toggle='collapse' "
                "or @data-bs-toggle='collapse']"
            )
        )

        for button in accordion_buttons:

            title = button.text.strip()

            href = button.get_attribute(
                "href"
            )

            if (
                not href
                or "#" not in href
            ):
                continue

            target = href.split(
                "#",
                1
            )[-1]

            if (
                not title
                or not target
            ):
                continue

            current_section = {
                "section_title":
                    title.upper(),
                "content": []
            }

            self.driver.execute_script(
                """
                var el =
                    document.getElementById(arguments[0]);

                if (el) {
                    el.classList.add("in");
                    el.style.display = "block";
                }
                """,
                target
            )

            time.sleep(0.2)

            try:

                collapse_div = (
                    self.driver.find_element(
                        By.ID,
                        target
                    )
                )

            except Exception:

                continue

            # TABLE
            tables = (
                collapse_div.find_elements(
                    By.TAG_NAME,
                    "table"
                )
            )

            for table in tables:

                rows = (
                    table.find_elements(
                        By.XPATH,
                        ".//tr"
                    )
                )

                for row in rows:

                    cols = [
                        td.text.strip()
                        for td in row.find_elements(
                            By.XPATH,
                            ".//th | .//td"
                        )
                        if td.text.strip()
                    ]

                    if cols:

                        current_section[
                            "content"
                        ].append(
                            " | ".join(cols)
                        )

            # LIST ITEMS
            lis = (
                collapse_div.find_elements(
                    By.TAG_NAME,
                    "li"
                )
            )

            for li in lis:

                text = li.text.strip()

                if text:

                    current_section[
                        "content"
                    ].append(text)

            # PARAGRAPHS
            paragraphs = (
                collapse_div.find_elements(
                    By.TAG_NAME,
                    "p"
                )
            )

            for paragraph in paragraphs:

                text = paragraph.text.strip()

                if text:

                    current_section[
                        "content"
                    ].append(text)

            if current_section["content"]:

                sections.append(
                    current_section
                )

        return {
            "url": url,
            "title": page_title,
            "sections": sections
        }

    # =====================================================
    # DISCOVER COURSE LINKS
    # =====================================================

    def scrape_from_about_page(
        self,
        about_url
    ):

        all_data = []

        self.driver.get(
            about_url
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        # -------------------------------------------------
        # STATIC NAV LINKS
        # -------------------------------------------------

        static_links = []

        nav_links = (
            self.driver.find_elements(
                By.XPATH,
                "//ul[contains(@class,'nav')]//a[@href]"
            )
        )

        for a in nav_links:

            href = a.get_attribute(
                "href"
            )

            if not href:
                continue

            href_lower = href.lower()

            if any(
                key in href_lower
                for key in [
                    "about-us",
                    "contact-us"
                ]
            ):

                static_links.append(
                    urljoin(
                        about_url,
                        href
                    )
                )

        static_links = list(
            dict.fromkeys(
                static_links
            )
        )

        # -------------------------------------------------
        # COURSE LINKS
        # -------------------------------------------------

        buttons = (
            self.driver.find_elements(
                By.XPATH,
                """
                //a[contains(@class,'course_view_more_btn')]
                |
                //div[contains(@class,'c_cat_box')]
                //a[contains(@class,'c_cat_more_btn')]
                """
            )
        )

        course_links = []

        course_links.extend(
            static_links
        )

        for button in buttons:

            href = button.get_attribute(
                "href"
            )

            if not href:
                continue

            course_links.append(
                urljoin(
                    about_url,
                    href
                )
            )

        course_links = list(
            dict.fromkeys(
                course_links
            )
        )

        print(
            f"[INFO] Found "
            f"{len(course_links)} total links"
        )

        for link in course_links:

            print(
                f"[SCRAPING] {link}"
            )

            data = self.scrape(
                link
            )

            if not data:
                continue

            if isinstance(
                data,
                list
            ):

                all_data.extend(
                    data
                )

            else:

                all_data.append(
                    data
                )

        with open(
            "output.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                all_data,
                file,
                indent=2,
                ensure_ascii=False
            )

        self.driver.quit()

        return all_data