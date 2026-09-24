import json

from pathlib import Path

from scraping.Scraper import Courses_scraper
from scraping.internship_scraper import InternshipScraper

from config import OUTPUT_JSON


def run_scraping():

    all_data = []

    # =====================================================
    # COURSE / ABOUT / CONTACT SCRAPER
    # =====================================================

    course_scraper = Courses_scraper()

    try:

        course_data = (
            course_scraper.scrape_from_about_page(
                "https://www.sunbeaminfo.in/"
            )
        )

        if course_data:

            all_data.extend(
                course_data
            )

    finally:

        try:
            course_scraper.driver.quit()
        except Exception:
            pass

    # =====================================================
    # INTERNSHIP SCRAPER
    # =====================================================

    internship_scraper = InternshipScraper()

    try:

        internship_data = (
            internship_scraper.scrape()
        )

        if internship_data:

            all_data.append(
                internship_data
            )

    finally:

        internship_scraper.close()

    # =====================================================
    # SAVE
    # =====================================================

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"[SUCCESS] Saved "
        f"{len(all_data)} pages to "
        f"{OUTPUT_JSON}"
    )

    return all_data