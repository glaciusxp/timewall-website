# TimeWall — sito vetrina

Sito statico in italiano e inglese, tema Ardesia e Azzurro. HTML, CSS e JavaScript senza dipendenze di runtime o servizi esterni per le risorse del sito.

## Struttura

- `dist/`: sito pronto da servire con qualsiasi hosting statico; include APK.
- `build.py`: genera le sei pagine per ciascuna lingua e l’ingresso italiano.
- `public/`: immagini, stili, script, testi delle licenze e APK originali da copiare nel sito.
- `content/it.xml`, `content/en.xml`: testi privacy e crediti derivati dalle risorse della release Android verificata.
- `release.json`: versione e numero build.

## Rigenerazione

Richiede Python 3, senza pacchetti aggiuntivi:

```sh
python3 build.py
```

Per l’anteprima locale:

```sh
python3 -m http.server 8080 --directory dist
```

## Completamento prima della distribuzione definitiva

- Per aggiornare l’APK scaricabile, sostituire `public/downloads/TimeWall-Dashboard.apk` con l’output di `assembleSiteFreeWebsite`.
- Aggiornare `release.json` e la data del file nella pagina download in `build.py`.
- Compilare il changelog in `build.py` con le note effettive delle versioni.
- Quando disponibile, sostituire il pulsante Google Play disabilitato con un collegamento alla scheda ufficiale.
- Aggiornare la sezione licenza quando l’autore avrà scelto le condizioni di distribuzione.
- L’APK incluso è TimeWall Free per il sito, versione 0.102, build 102, con ID di collaudo `it.timewall.dashboard.sitefree`.
- Gli screenshot originali provengono dalla versione 0.101, con dati dimostrativi. La dashboard inglese è disponibile; gli altri screenshot originali sono in italiano.
- Il testo privacy dell’app riprende l’informativa già presente nei sorgenti del 20 novembre 2026; la sezione sito descrive il comportamento di queste pagine statiche.

## Riscontro sui riferimenti ai calendari

Nei sorgenti Android recuperati esiste ancora la chiave `google_calendar` in nove traduzioni (`src/main/res/values*/strings.xml`, riga 50); non sono stati trovati utilizzi della chiave nel codice Java. Sono presenti riferimenti tecnici separati al provider TLS di sistema in `platform/tls/PlayServicesTls.java`, al formatter di sviluppo e nei copyright dei font. Il sito presenta esclusivamente calendari iCal pubblici, indipendenti dal provider. I sorgenti Android non sono stati modificati.
