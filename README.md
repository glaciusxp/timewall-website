# TimeWall — sito vetrina

Sito statico in italiano e inglese, tema Ardesia e Azzurro. HTML, CSS e JavaScript senza dipendenze di runtime o servizi esterni per le risorse del sito.

## Struttura

- `dist/`: sito pronto da servire con qualsiasi hosting statico; include APK.
- `build.py`: genera le sette pagine per ciascuna lingua e l’ingresso italiano.
- `public/`: immagini, stili, script, testi delle licenze e APK originali da copiare nel sito.
- `content/it.xml`, `content/en.xml`: testi privacy e crediti derivati dalle risorse della release Android verificata.
- `release.json`: versione e numero build.

## Rigenerazione

Richiede Python 3, senza pacchetti aggiuntivi:

```sh
python3 build.py
```

La build valida i metadati e l'integrità dell'APK indicato in `release.json`.
Genera il sito in una directory temporanea accanto a `dist/`. Se la generazione
fallisce, la copia precedente di `dist/` resta utilizzabile. Al termine di una
build riuscita, la nuova directory sostituisce quella precedente.

Per l’anteprima locale:

```sh
python3 -m http.server 8080 --directory dist
```

## Distribuzione

- L’APK pubblico e i relativi metadati sono definiti in `release.json`. Il workflow di rilascio del repository dell’app li aggiorna quando viene pubblicato un tag per il sito.
- La pagina Download mostra le funzioni della versione scaricabile in base al numero di build. La home e la guida possono presentare funzioni in test, con un’indicazione della loro disponibilità.
- Aggiornare il collegamento a Google Play quando la scheda sarà pubblica.
- Il codice di TimeWall è distribuito con licenza MIT. Le risorse di terze parti mantengono le rispettive licenze.
- La galleria e il Quick Start usano catture in italiano e inglese da emulatore Android con dati dimostrativi. Le catture orizzontali provengono dalla build 110. Quelle verticali includono i ritocchi alla dashboard successivi alla build 111.
- La pagina Privacy riprende l’informativa Android e descrive anche l’esportazione manuale delle impostazioni e il comportamento del sito statico.

TimeWall supporta feed iCal pubblici via HTTPS, indipendentemente dal provider.
