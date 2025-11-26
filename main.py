from playwright.sync_api import sync_playwright, Playwright
import requests
from bs4 import BeautifulSoup


def run(playwright: Playwright):
    context = playwright.chromium.launch_persistent_context(
        user_data_dir="/tmp/brave-playwright",  # qualunque cartella
        executable_path="/usr/bin/brave",
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
        ],
    )
    page = context.new_page()
    ## TODO: Far si che non si crei la pagina iniziale blank
    ## IDEA: -non usare persistent_context?? (dopo potrebbe non tenere i cookie però...)
    ##
    context.clear_cookies()
    page.goto("https://unistudium.unipg.it/unistudium/local/login/index.php")
    page.wait_for_url("https://unistudium.unipg.it/unistudium/")
    moodle_cookie = next(
        (
            c
            for c in context.cookies()
            if c["name"] == "MoodleSessionpg_unistudium_prod"
        ),
        None,
    )
    page.close()
    return moodle_cookie["value"]


def course(cookie: dict, url):
    cookies = dict(MoodleSessionpg_unistudium_prod=cookie)
    r = requests.get(url, cookies=cookies)

    soup = BeautifulSoup(r.text, "html.parser")

    ##print(r.text)
    sections = []

    for section in soup.select("li.section.course-section"):
        nome_sezione = section.select_one("h3.sectionname a").get_text(strip=True)

        activity = []

        for item in section.select("li.activity"):
            link_tag = item.select_one("a")
            if not link_tag:
                continue

            titolo = link_tag.get_text(strip=True)
            url = link_tag["href"]

            activity.append({"titolo": titolo, "url": url})

        sections.append({"sezione": nome_sezione, "attività": activity})

    sectionCount = 0
    activityCount = 0
    for sec in sections:
        print("SEZIONE ", sectionCount, ": ", sec["sezione"])
        for att in sec["attività"]:
            print(sectionCount, "-", activityCount, att["titolo"], "→", att["url"])
            activityCount += 1
        print("\n")
        activityCount = 0
        sectionCount += 1

    values = input("Selezione [SEZIONE]-[ATTIVITA'] -> ").split("-")
    print(sections[int(values[0])]["attività"][int(values[1])]["url"])


with sync_playwright() as playwright:
    cookie = run(playwright)
    url = "https://unistudium.unipg.it/unistudium/"
    cookies = dict(MoodleSessionpg_unistudium_prod=cookie)
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    corsi = []

    corsi = [h3.get_text(strip=True) for h3 in soup.select("h3.coursename a")]

    links = [a["href"] for a in soup.select("h3.coursename a")]

    cnt = 0
    for nome in corsi:
        print(cnt, "] ", nome)
        cnt += 1

    corso = int(input("Numero corso su cui vuoi entrare -> "))
    course(cookie, links[corso])
