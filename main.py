from playwright.sync_api import sync_playwright, Playwright
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
import re
from typing import Optional, Dict, List, Tuple
import time
class UniStudiumDownloader:
    """Classe per gestire il download di materiali da UniStudium"""
    
    BASE_URL = "https://unistudium.unipg.it/unistudium/"
    LOGIN_URL = "https://unistudium.unipg.it/unistudium/local/login/index.php"
    COOKIE_NAME = "MoodleSessionpg_unistudium_prod"
    
    def __init__(self, download_dir: str = "downloads"):
        self.cookie: Optional[str] = None
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    def get_browser_cookie(self, playwright: Playwright) -> str:
        """Ottiene il cookie di sessione tramite autenticazione browser"""
        browsers = [
            ("Brave", playwright.chromium, "/usr/bin/brave"),
            ("Firefox", playwright.firefox, None),
            ("Opera", playwright.chromium, "/usr/bin/opera"),
            ("Chromium", playwright.chromium, None),
            ("WebKit", playwright.webkit, None),
        ]

        context = None
        for name, engine, path in browsers:
            try:
                launch_args = {
                    "user_data_dir": "/tmp/playwright-user-data",
                    "headless": False,
                }
                if path:
                    launch_args["executable_path"] = path
                    
                context = engine.launch_persistent_context(**launch_args)
                print(f"✓ Browser utilizzato: {name}")
                break
            except Exception as e:
                print(f"✗ {name} non disponibile: {e}")
                continue

        if context is None:
            raise RuntimeError("Nessun browser disponibile per Playwright!")

        page = context.new_page()
        print("Effettua il login su UniStudium...")
        page.goto(self.LOGIN_URL)
        
        timeout = 120  # secondi
        start = time.time()

        moodle_cookie = None
        cookies = context.cookies()
        moodle_cookie = next(
            (c for c in cookies if c["name"] == self.COOKIE_NAME),
            None,
        )
        current_moodle_cookie = None
        while time.time() - start < timeout:
            cookies = context.cookies()
            current_moodle_cookie = next(
                (c for c in cookies if c["name"] == self.COOKIE_NAME),
                None,
            )
            if moodle_cookie != current_moodle_cookie:
                print(current_moodle_cookie)
                break
            time.sleep(0.2)
        if not current_moodle_cookie:
            raise TimeoutError("Cookie di login non trovato entro il timeout")
        
        page.close()
        context.close()
        
        return current_moodle_cookie["value"]
    
    def get_cookies_dict(self) -> Dict[str, str]:
        """Restituisce il dizionario dei cookie per le richieste"""
        return {self.COOKIE_NAME: self.cookie}
    
    def fetch_courses(self) -> List[Tuple[str, str]]:
        """Recupera la lista dei corsi disponibili"""
        response = requests.get(self.BASE_URL, cookies=self.get_cookies_dict())
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        courses = []
        
        for h3 in soup.select("h3.coursename a"):
            name = h3.get_text(strip=True)
            link = h3["href"]
            courses.append((name, link))
            
        return courses
    
    def display_courses(self, courses: List[Tuple[str, str]]) -> int:
        """Mostra i corsi e richiede la selezione dell'utente"""
        print("\n" + "="*80)
        print("CORSI DISPONIBILI")
        print("="*80)
        
        for idx, (name, _) in enumerate(courses):
            print(f"{idx:2d} | {name}")
        
        print("="*80)
        
        while True:
            try:
                choice = input("\nSeleziona il numero del corso (o 'q' per uscire): ").strip()
                if choice.lower() == 'q':
                    return -1
                    
                choice_int = int(choice)
                if 0 <= choice_int < len(courses):
                    return choice_int
                else:
                    print(f"❌ Inserisci un numero tra 0 e {len(courses) - 1}")
            except ValueError:
                print("❌ Inserisci un numero valido o 'q' per uscire")
    
    def fetch_course_sections(self, course_url: str) -> List[Dict]:
        """Recupera le sezioni e le attività di un corso"""
        response = requests.get(course_url, cookies=self.get_cookies_dict())
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        sections = []

        for section in soup.select("li.section.course-section"):
            section_name_tag = section.select_one("h3.sectionname a")
            if not section_name_tag:
                continue
                
            section_name = section_name_tag.get_text(strip=True)
            activities = []

            for item in section.select("li.activity"):
                link_tag = item.select_one("a")
                if not link_tag or not link_tag.get("href"):
                    continue

                title = link_tag.get_text(strip=True)
                url = link_tag["href"]
                activities.append({"title": title, "url": url})

            if activities:  # Aggiungi solo sezioni con attività
                sections.append({"name": section_name, "activities": activities})

        return sections
    
    def display_sections(self, sections: List[Dict]) -> Tuple[int, int]:
        """Mostra le sezioni e richiede la selezione dell'utente"""
        print("\n" + "="*80)
        print("CONTENUTI DEL CORSO")
        print("="*80)
        
        for sec_idx, section in enumerate(sections):
            print(f"\n📁 SEZIONE {sec_idx}: {section['name']}")
            print("-" * 80)
            for act_idx, activity in enumerate(section["activities"]):
                print(f"  {sec_idx}-{act_idx} | {activity['title']}")
        
        print("="*80)
        
        while True:
            choice = input("\nSelezione [SEZIONE]-[ATTIVITÀ] (o 'q' per tornare): ").strip()
            
            if choice.lower() == 'q':
                return -1, -1
            
            match = re.match(r'(\d+)-(\d+)', choice)
            if not match:
                print("❌ Formato non valido. Usa: SEZIONE-ATTIVITÀ (es: 0-3)")
                continue
            
            sec_idx, act_idx = int(match.group(1)), int(match.group(2))
            
            if 0 <= sec_idx < len(sections) and 0 <= act_idx < len(sections[sec_idx]["activities"]):
                return sec_idx, act_idx
            else:
                print("❌ Selezione non valida. Riprova.")
    
    def sanitize_filename(self, filename: str) -> str:
        """Rimuove caratteri non validi dal nome file"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename[:255]  # Limita la lunghezza
    
    def download_file(self, url: str, filename: str = None) -> bool:
        """Scarica un file dall'URL specificato"""
        try:
            print(f"\n📥 Download da: {url}")
            response = requests.get(url, cookies=self.get_cookies_dict(), stream=True)
            response.raise_for_status()
            
            # Determina il nome del file
            if not filename:
                content_disposition = response.headers.get("Content-Disposition", "")
                if "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[1].strip().strip('"').strip("'")
                else:
                    filename = url.split("/")[-1].split("?")[0] or "download"
            
            filename = self.sanitize_filename(filename)
            filepath = self.download_dir / filename
            
            # Gestisci file con stesso nome
            counter = 1
            original_stem = filepath.stem
            while filepath.exists():
                filepath = self.download_dir / f"{original_stem}_{counter}{filepath.suffix}"
                counter += 1
            
            # Scarica con progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, "wb") as file:
                if total_size:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            
            print(f"✓ Salvato in: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Errore durante il download: {e}")
            return False
    
    def run(self):
        """Esegue il loop principale dell'applicazione"""
        print("="*80)
        print(" UniStudium Downloader ".center(80, "="))
        print("="*80)
        
        with sync_playwright() as playwright:
            try:
                self.cookie = self.get_browser_cookie(playwright)
                print("✓ Autenticazione completata\n")
            except Exception as e:
                print(f"❌ Errore durante l'autenticazione: {e}")
                return
        
        while True:
            try:
                courses = self.fetch_courses()      
                if not courses:
                    print("❌ Nessun corso trovato")
                    break
                course_idx = self.display_courses(courses)
                if course_idx == -1:
                    break
                course_name, course_url = courses[course_idx]
                print(f"\n📚 Corso selezionato: {course_name}")
                
                # Loop per il corso selezionato
                while True:
                    sections = self.fetch_course_sections(course_url)
                    if not sections:
                        print("❌ Nessun contenuto trovato in questo corso")
                        break
                    
                    sec_idx, act_idx = self.display_sections(sections)
                    if sec_idx == -1:
                        break
                    
                    activity = sections[sec_idx]["activities"][act_idx]
                    print(f"\n📄 Selezionato: {activity['title']}")
                    
                    self.download_file(activity["url"])
                    
                    # Chiedi se continuare
                    continue_choice = input("\n🔄 Scaricare altro da questo corso? (s/n): ").strip().lower()
                    if continue_choice != 's':
                        break
            except KeyboardInterrupt:
                print("\n\n⚠️ Interruzione da tastiera")
                break
            except Exception as e:
                print(f"❌ Errore: {e}")
                break


if __name__ == "__main__":
    downloader = UniStudiumDownloader()
    downloader.run()