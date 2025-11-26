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
    print(r.text)


with sync_playwright() as playwright:
    cookie = run(playwright)
    url = "https://unistudium.unipg.it/unistudium/"
    cookies = dict(MoodleSessionpg_unistudium_prod=cookie)
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")

    corsi = []
    
    corsi=[h3.get_text(strip=True) for h3 in soup.select("h3.coursename a")]

    links = [a["href"] for a in soup.select("h3.coursename a")]
    print(links[0])
    
    cnt = 0
    for nome in corsi:
        print(cnt, "] ", nome, " [link: ", links[cnt], "]")
        cnt = cnt + 1
    corso = int(input("Numero corso su cui vuoi entrare -> "))
    course(cookie, links[corso])
