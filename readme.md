# Unistudium Downloader

Un tool Python per scaricare materiale didattico dalla piattaforma Unistudium dell'Università degli Studi di Perugia.

Analizzando le richieste fatte da unistudium nel corso della navigazione, ho visto che vengono caricati ad ogni nuova pagina dai 2 ai 6 file dinamici non utili, come librerie js o file css pesantissimi che rallentano la navigazione.

In più: 
- mi fa schifo graficamente e non è faicle (se non impossibile, per motivi di sicurezza) replicare l'autenticazione SAML da 0
- UniPG non espone l'api di Moodle quindi non si può ricreare un sito personalizzato

Quindi ho voluto fare questo programma che runna tranquillamente su un qualsiasi terminale Linux per poter usare Unistudium senza interfaccia web.


## Descrizione

Questo progetto permette di navigare attraverso i corsi disponibili su Unistudium e scaricare facilmente i file delle attività didattiche. Utilizza Playwright per l'autenticazione automatica tramite browser e requests per il download dei file.

## Requisiti

- **Sistema Operativo**: Arch Linux o derivati (utilizza `yay` come package manager)
- **Python**: 3.7 o superiore
- **Browser**: Almeno uno tra Brave, Chromium, Firefox, WebKit o Opera

## Installazione

### 1. Clona o scarica il repository

```bash
git clone <url-repository>
cd <nome-directory>
```

### 2. Esegui lo script di installazione

```bash
python3 install.py
```

Lo script installerà automaticamente:

- python-bs4 (BeautifulSoup4)
- python-requests
- python-playwright
- python-tqdm
- I browser necessari per Playwright

## Utilizzo

### Avvio del programma

```bash
python3 main.py
```

### Flusso di utilizzo

1. **Autenticazione**: Si aprirà automaticamente una finestra del browser. Effettua il login con le tue credenziali Unistudium.

2. **Selezione del corso**: Dopo il login, ti verrà mostrata la lista dei tuoi corsi numerati. Inserisci il numero del corso desiderato.

3. **Navigazione delle sezioni**: Verranno visualizzate tutte le sezioni del corso con le relative attività nel formato:

   ```
   SEZIONE-ATTIVITÀ Titolo → URL
   ```

4. **Download del file**: Inserisci la selezione nel formato `SEZIONE-ATTIVITÀ` (es: `0-1` per la seconda attività della prima sezione).

5. **Tornare alla lista corsi**: Inserisci `q` quando richiesto per tornare alla selezione dei corsi.

## Caratteristiche

- ✅ Autenticazione automatica tramite browser
- ✅ Supporto multi-browser (Brave, Chromium, Firefox, WebKit, Opera)
- ✅ Navigazione interattiva dei corsi
- ✅ Barra di progresso durante il download
- ✅ Salvataggio automatico dei file con nome originale

## Note tecniche

- Il cookie di sessione viene estratto automaticamente dopo il login
- I file vengono salvati nella directory corrente con il nome originale
- Il browser viene aperto in modalità non-headless per permettere l'autenticazione
- I dati temporanei del browser sono salvati in `/tmp/playwright-user-data`

## Limitazioni

- Funziona solo su sistemi Arch Linux (per via di `yay`)
- Richiede almeno un browser compatibile installato
- Il download è sequenziale (un file alla volta)

## Possibili miglioramenti futuri

- Supporto per altri package manager (apt, dnf, brew)
- Utilizzo di virtual environment per l'installazione
- Download batch di multiple attività
- Interfaccia grafica

## Troubleshooting

### Errore "Nessun browser disponibile"

Assicurati di avere almeno uno dei browser supportati installato sul sistema.

### Errore durante l'installazione

Verifica di avere `yay` installato e configurato correttamente su Arch Linux.

### Problemi di autenticazione

Controlla che le credenziali Unistudium siano corrette e che la connessione internet sia stabile.

## Contributi

I contributi sono benvenuti! Sentiti libero di aprire issue o pull request.
