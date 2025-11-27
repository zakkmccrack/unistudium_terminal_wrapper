from playwright.sync_api import sync_playwright, Playwright
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def run(p: Playwright):
    browsers = [
        ("Brave", p.chromium, "/usr/bin/brave"),
        ("Chromium", p.chromium, None),
        ("Firefox", p.firefox, None),
        ("WebKit", p.webkit, None),
        ("Opera", p.chromium, "/usr/bin/opera"),
    ]

    for name, engine, path in browsers:
        try:
            launch_args = {
                "user_data_dir": "/tmp/playwright-user-data",
                "headless": False,
            }
            if path:
                launch_args["executable_path"] = path
            context = engine.launch_persistent_context(**launch_args)
            print(f"Browser usato: {name}")
            break
        except Exception as e:
            print(f"{name} non disponibile: {e}")
            continue

    if context is None:
        raise RuntimeError("Nessun browser disponibile per Playwright!")

    page = context.new_page()
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


def read_course(max: int):
    while True:
        corso = input("Numero corso su cui vuoi entrare -> ")
        if corso.isdigit():
            corso = int(corso)
            if corso < max and corso >= 0:
                return corso
        print("Non è nella tua lista di corsi!")
        print(
            "O hai passato troppi esami oppure...devi ripassare gli insiemi numerici per analisi 1"
        )


def read_selection(cookie: dict):
    while True:
        values = input(
            "Selezione [SEZIONE]-[ATTIVITA'] (INVIA q PER TORNARE ALLA LISTA CORSI) -> "
        ).split("-")
        if len(values) == 2:
            return values
        if len(values) == 1:
            if values[0] == "q":
                get_course(cookie)
        print("Formato non valido, riprova")


def get_course(cookie):
    cookies = dict(MoodleSessionpg_unistudium_prod=cookie)
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")

    corsi = [h3.get_text(strip=True) for h3 in soup.select("h3.coursename a")]

    links = [a["href"] for a in soup.select("h3.coursename a")]

    cnt = 0
    for nome in corsi:
        print(cnt, "] ", nome)
        cnt += 1

    corso = read_course(cnt)
    course(cookie, links[corso])


def course(cookie: dict, mainUrl):
    cookies = dict(MoodleSessionpg_unistudium_prod=cookie)
    r = requests.get(mainUrl, cookies=cookies)

    soup = BeautifulSoup(r.text, "html.parser")

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

    values = read_selection(cookie)
    print(sections[int(values[0])]["attività"][int(values[1])]["url"])
    remoteUrl = sections[int(values[0])]["attività"][int(values[1])]["url"]
    print(remoteUrl)
    response = requests.get(remoteUrl, cookies=cookies, stream=True)

    content_type = response.headers.get("Content-Disposition")
    filename = ""
    if content_type and "filename=" in content_type:
        filename = content_type.split("filename=")[1].strip().strip('"').strip("'")
    else:
        filename = url.split("/")[-1]

    with open(filename, "wb") as file:
        for chunk in tqdm(response.iter_content(chunk_size=1024), unit="KB"):
            file.write(chunk)

    course(cookie, mainUrl)


with sync_playwright() as playwright:
    cookie = run(playwright)
    url = "https://unistudium.unipg.it/unistudium/"

    get_course(cookie)
