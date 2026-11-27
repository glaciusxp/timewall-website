from datetime import date
from pathlib import Path
import shutil,html,xml.etree.ElementTree as ET,json,hashlib
from tempfile import TemporaryDirectory, mkdtemp
from zipfile import ZipFile
ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'

def render(OUT):
 AS = OUT / 'assets'
 release = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
 release_date = date.fromisoformat(release['release_date'])
 if not isinstance(release['version'], str) or not release['version'].strip():
  raise ValueError('release.json: version must be a non-empty string')
 if type(release['build']) is not int or release['build'] < 1:
  raise ValueError('release.json: build must be a positive integer')
 apk_source = ROOT / 'public/downloads/TimeWall-Dashboard.apk'
 if release['apk_source'] != apk_source.relative_to(ROOT).as_posix():
  raise ValueError('release.json: apk_source must match the public download path')
 if not apk_source.is_file():
  raise FileNotFoundError(f'Missing release APK: {apk_source}')
 with ZipFile(apk_source) as apk_zip:
  if 'AndroidManifest.xml' not in apk_zip.namelist() or apk_zip.testzip() is not None:
   raise ValueError(f'Invalid release APK: {apk_source}')
 shutil.copytree(ROOT / 'public', OUT)
 months={
  'it': 'gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre'.split(),
  'en': 'January February March April May June July August September October November December'.split(),
 }
 notices=[p.name for p in (AS/'licenses').glob('*.txt')]
 def strings(lang):
  p=ROOT/'content'/(lang+'.xml')
  return {x.attrib['name']:''.join(x.itertext()) for x in ET.parse(p).getroot() if x.tag=='string'}
 def esc(s): return html.escape(str(s))
 def card(title,body): return f'<article class="feature"><h3>{title}</h3><p>{body}</p></article>'
 for lang in ['it','en']:
  it=lang=='it'; T=lambda a,b:a if it else b
  apk_date=f'{release_date.day} {months[lang][release_date.month-1]} {release_date.year}'
  pages={'index':T('Home','Home'),'quick-start':'Quick start','download':'Download','info':T('Il progetto','The project'),'donate':T('Dona','Donate'),'privacy':'Privacy','credits':T('Licenze e crediti','Licences & credits')}
  d=OUT/lang;d.mkdir(exist_ok=True)
  def link(p):return p+'.html'
  def pic(file,alt,cls='',lazy=True):return f'<img class="{cls}" src="../assets/{file}" alt="{esc(alt)}" width="1920" height="1200" '+('loading="lazy" ' if lazy else 'fetchpriority="high" ')+ '>'
  def screen(file,alt):return f'<a class="shot" href="../assets/{file}" data-lightbox>{pic(file,alt)}<span>{alt}<span class="zoom">{T("Ingrandisci","Enlarge")}</span></span></a>'
  def cta():return f'<section class="cta"><div><span class="eyebrow">{T("UN NUOVO POSTO PER IL TUO TABLET","A NEW PURPOSE FOR YOUR TABLET")}</span><h2>{T("Fai spazio alla tua giornata.","Make room for your day.")}</h2></div><a class="button" href="download.html">{T("Scarica TimeWall","Download TimeWall")}</a></section>'
  hero_file='01-agenda-scuro-it.png' if it else '07-agenda-scuro-en.png'
  legacy_download = release['build'] < 104
  has_backup_and_focus = release['build'] >= 107
  preview_note = '' if has_backup_and_focus else T(
   '<p class="fine">Questa pagina include le funzioni della versione in test. Le funzioni dell’APK pubblico sono elencate nella pagina <a href="download.html">Download</a>.</p>',
   '<p class="fine">This page includes features from the test version. See <a href="download.html">Downloads</a> for the features in the public APK.</p>'
  )
  widget_items = [
   ('clock', 408, 228, T('Orologio', 'Clock'),
    T('Ora e data al centro, con formato e font configurabili.', 'Centred time and date, with configurable formats and font.')),
   ('whats_next', 444, 232, 'What’s next',
    T('Mostra l’appuntamento in corso o il prossimo di oggi. Indica quando inizierà o quando finirà.', 'See the current appointment or the next one today, with its start or end time.')),
   ('agenda', 444, 380, 'Agenda',
    T('Consulta gli appuntamenti di oggi e dei prossimi giorni.', 'Browse today’s appointments and upcoming events.')),
   ('weather', 408, 256, T('Meteo', 'Weather'),
    T('Temperatura e condizioni della località impostata nella Dashboard. I dettagli si adattano allo spazio disponibile.',
      'Temperature and conditions for the location set in the dashboard. The detail adapts to the space available.')),
  ]
  widget_cards = ''.join(
   f'<article class="feature widget-preview"><h3>{title}</h3>'
   f'<img src="../assets/{key}_widget_preview.png" alt="" width="{width}" height="{height}" loading="lazy">'
   f'<p>{description}</p></article>'
   for key, width, height, title, description in widget_items
  )
  widgets = f"""<section class="section" id="widgets" aria-labelledby="widgets-title">
  <div class="section-heading">
  <h2 id="widgets-title">{T('La dashboard sulla schermata Home','Bring the dashboard to your home screen')}</h2>
  <p>{T('Disponi i quattro widget come preferisci. Puoi aggiungere più istanze di Agenda e What’s next, scegliendo calendari diversi per ciascuna.',
        'Arrange the four widgets however you like. Add multiple Agenda and What’s next widgets and choose different calendars for each.')}</p>
  </div><div class="widget-previews">{widget_cards}</div></section>"""
  home=f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">{T('LA TUA GIORNATA. A COLPO D’OCCHIO.','YOUR DAY. AT A GLANCE.')}</p><h1>{T('Il tuo tempo,<br>in primo <em>piano.</em>','Your time,<br>in <em>focus.</em>')}</h1><p class="lead">{T('Vedi a colpo d’occhio l’impegno in corso o il prossimo di oggi. TimeWall trasforma anche un vecchio tablet Android in una dashboard da scrivania, con orologio e agenda sempre in vista.','See what’s happening now or what’s next today at a glance. TimeWall turns even an older Android tablet into a desk dashboard with your clock and agenda in view.')}</p><div class="actions"><a class="button" href="download.html">{T('Scarica TimeWall','Download TimeWall')}</a><a class="button secondary" href="#widgets">{T("Scopri i widget","Explore the widgets")}</a></div><p class="fine">{T("Gratuita e open source","Free and open source")} <span>·</span> Android 4.4+ <span>·</span> {T('Collaudata su Asus TF303CL','Tested on Asus TF303CL')}</p></div><div class="hero-art"><div class="tablet"><a href="../assets/{hero_file}" data-lightbox aria-label="{T('Ingrandisci la dashboard','Enlarge the dashboard')}">{pic(hero_file,T('Dashboard TimeWall con orologio, meteo e agenda','TimeWall dashboard with clock, weather and agenda'),lazy=False)}</a></div><p class="image-note">{T('Anteprima della dashboard','Dashboard preview')}</p></div></section>
  {preview_note}
  <div class="benefit-bar"><span>{T('Calendari iCal pubblici','Public iCal calendars')}</span><span>{T('Nessun account TimeWall','No TimeWall account')}</span><span>{T('Evento in corso o prossimo','Current or next event')}</span></div>
  <section class="section"><div class="section-heading"><p class="eyebrow">{T('MENO TOCCHI, PIÙ CHIAREZZA','FEWER TAPS, MORE CLARITY')}</p><h2>{T('Tutto ciò che serve.<br>Uno sguardo soltanto.','Everything you need.<br>Just a glance away.')}</h2><p>{T('Sul tavolo, in cucina o accanto alla scrivania: un punto di riferimento per gli impegni di ogni giorno.','On a table, in the kitchen or beside your desk: a shared view of what the day has in store.')}</p></div><div class="features">{card(T('Il tempo, ben visibile','Time, clearly displayed'),T('Un grande orologio con data e formato personalizzabile. Ora, data e meteo si adattano allo spazio disponibile.','A large clock with date and customisable format. The clock, date and weather adapt to the space available.'))}{card(T('L’impegno che conta adesso','The event that matters now'),T('Il quadrante In primo piano mostra l’evento in corso o il prossimo di oggi, anche se è più tardi. Nell’Agenda trovi gli altri appuntamenti, gli eventi di tutta la giornata e i giorni successivi.','The In focus panel shows the current event or the next one today, even if it starts later. The agenda alongside shows other appointments, all-day events and upcoming days.'))}{card(T('Una seconda vita per il tablet','A second life for your tablet'),T('Metti in orizzontale un tablet che usi poco e tienilo sulla scrivania come pannello per gli impegni di ogni giorno.','Place a tablet you rarely use in landscape on your desk and turn it into an everyday display for your plans.'))}</div></section>
  {widgets}
  <section class="section gallery-section" id="screenshots"><div class="section-heading inline"><div><p class="eyebrow">{T('DENTRO TIMEWALL','A LOOK INSIDE')}</p><h2>{T('Un’app, il tuo stile.','One app. Your style.')}</h2></div><p>{T('Temi chiari e scuri, calendari a colori e dettagli sempre a portata di mano.','Light and dark themes, colourful calendars and details within easy reach.')}</p></div><div class="gallery">{screen(hero_file,T('La dashboard, in scuro','The dashboard, in dark mode'))}{screen('02-agenda-chiaro-it.png',T('La leggerezza del tema chiaro','A fresh look in light mode'))}{screen('03-calendari-it.png',T('Tutti i tuoi calendari','All your calendars'))}{screen('04-personalizzazione-it.png',T('Un aspetto che ti somiglia','A look that feels like you'))}{screen('05-meteo-it.png',T('Il meteo della tua località','Weather for your chosen location'))}{screen('06-dettaglio-evento-it.png',T('Ogni evento, nel dettaglio','Every event, in detail'))}</div><p class="fine">{T('Schermate dimostrative di TimeWall su tablet, acquisite con una versione precedente.','Tablet screenshots from an earlier version of TimeWall, with demo data. Some screens are in Italian.')}</p></section>
  <section class="split section"><div><p class="eyebrow">{T('UN TABLET, UNA NUOVA ABITUDINE','ONE TABLET, A NEW ROUTINE')}</p><h2>{T('Dai una nuova<br>giornata al tuo tablet.','Give your tablet<br>a new day.')}</h2></div><div><p class="lead">{T('TimeWall nasce per rendere utile anche un tablet che hai già. Una schermata orizzontale, semplice da consultare, che lascia spazio alle cose da fare.','TimeWall is built to give a tablet you already own a useful role. A landscape display that’s easy to check and gives your plans room to breathe.')}</p><a class="text-link" href="quick-start.html">{T('Configuralo in pochi passi','Set it up in a few steps')}</a></div></section>{cta()}'''
  steps=[(T('Installa e apri TimeWall','Install and open TimeWall'),T('Scarica l’APK di TimeWall dalla pagina Download e aprilo sul dispositivo. Se Android lo richiede, autorizza l’installazione per l’app con cui hai aperto il file. I nomi delle opzioni variano in base alla versione di Android. Avvia TimeWall e posiziona il tablet in orizzontale.','Get the TimeWall APK from the Download page and open it on your device. If Android prompts you, allow installation from the app used to open the file. Option names vary by Android version. Open TimeWall and place your tablet in landscape orientation.')),
  (T('Prepara il link iCal','Get your iCal link ready'),T('Dal servizio che ospita il calendario, copia l’indirizzo pubblico del feed iCal (.ics), accessibile tramite HTTPS senza login. Serve il link al feed, non alla pagina web del calendario. TimeWall legge i calendari: le modifiche agli eventi si fanno nel servizio di origine.','From your calendar provider, copy the public iCal (.ics) feed URL, accessible over HTTPS without signing in. Use the feed URL, not the calendar’s web page. TimeWall reads calendars: edit events in the original calendar service.')),
  (T('Aggiungi il tuo calendario','Add your calendar'),T('Apri il menu ⋮ e vai in Impostazioni → Calendari. Premi Aggiungi Calendario, inserisci un nome e l’indirizzo pubblico iCal, quindi scegli un colore. Salva la configurazione.','Open the ⋮ menu and go to Settings → Calendars. Choose Add Calendar, enter a name and the public iCal URL, then select a colour. Save your configuration.')),
  (T('Scegli come vederli','Make it your own'),T('In Impostazioni scegli la lingua, il font, il tema chiaro o scuro e i formati di ora e data. Apri un evento dalla dashboard per leggerne i dettagli.','In Settings, choose your language, font, light or dark theme, and time and date formats. Open an event from the dashboard to see its details.'))]
  backup_intro = T(
   'Nella versione in test, apri Impostazioni → Backup e ripristino per esportare o ripristinare le impostazioni della dashboard.',
   'In the test version, open Settings → Backup and restore to export or restore your dashboard settings.'
  ) if not has_backup_and_focus else T(
   'Apri Impostazioni → Backup e ripristino per esportare o ripristinare le impostazioni della dashboard.',
   'Open Settings → Backup and restore to export or restore your dashboard settings.'
  )
  backup_details = T(
   'Con Crea backup scegli dove salvare il file JSON. Per usare il file, seleziona Ripristina da file e conferma. Il backup include calendari, filtri, preferenze e l’eventuale sfondo. Le cache e le impostazioni dei widget sono escluse. Conserva il file con cura perché può contenere URL privati dei calendari in chiaro.',
   'Choose Create backup to select where to save the JSON file. To use it, select Restore from file and confirm. The backup includes calendars, filters, preferences and your background image, if set. Caches and widget settings are excluded. Keep the file safe because it can contain private calendar URLs in plain text.'
  )
  backup_help = f'<details><summary>{T("Come salvo le mie impostazioni?", "How do I save my settings?")}</summary><p>{backup_intro}</p><p>{backup_details}</p></details>'
  quick=f'<div class="page-intro"><p class="eyebrow">{T("SI PARTE DA QUI","START HERE")}</p><h1>{T("La tua dashboard,<br>in pochi passi.","Your dashboard,<br>in a few steps.")}</h1><p class="lead">{T("Un tablet Android, una connessione e il link del tuo calendario iCal pubblico. Sei pronto.","An Android tablet, an internet connection and your public iCal calendar link. You’re ready.")}</p></div><div class="guide-layout"><aside class="toc"><strong>{T("In questa guida","In this guide")}</strong>'+''.join(f'<a href="#step-{i}">{a}</a>' for i,(a,b) in enumerate(steps))+f'</aside><div class="prose">'+''.join(f'<section class="guide-step" id="step-{i}"><h2>{a}</h2><p>{b}</p></section>' for i,(a,b) in enumerate(steps))+f'<div class="notice">{T("Gli URL segreti danno accesso al calendario: non condividerli negli screenshot e usa solo feed che sei autorizzato a consultare.","Secret URLs provide access to a calendar: keep them out of screenshots and use only feeds you are authorised to access.")}</div><h2>{T("Serve una mano?","Need a hand?")}</h2><details><summary>{T("Non compaiono gli eventi","My events are not showing")}</summary><p>{T("Verifica che il link restituisca un file iCal su HTTPS senza autenticazione. Salva il calendario e usa Aggiorna calendari dalla dashboard. Controlla anche la connessione.","Check that the URL serves an iCal file over HTTPS without authentication. Save the calendar and use Refresh calendars on the dashboard. Also check your connection.")}</p></details><details><summary>{T("Cosa succede senza connessione?","What happens offline?")}</summary><p>{T("L’orologio continua a funzionare e i calendari già caricati vengono conservati nella cache locale. Servono internet e un aggiornamento riuscito per ricevere nuovi eventi.","The clock keeps working and previously loaded calendars are retained in local cache. An internet connection and a successful refresh are needed to receive new events.")}</p></details>{backup_help}<p><a href="mailto:andreapersano@gmail.com">andreapersano@gmail.com</a></p></div></div>'
  apk=OUT/'downloads/TimeWall-Dashboard.apk'; size=f'{apk.stat().st_size/1024/1024:.2f}'
  download_summary = (T('L’APK attualmente disponibile include orologio, agenda e un calendario iCal. La versione unificata arriverà con il prossimo rilascio.',
                        'The current APK includes the clock, agenda and one iCal calendar. The unified app will arrive with the next release.')
                      if legacy_download else
                      T('Scarica TimeWall per Android con tutti i widget e le funzioni della dashboard.',
                        'Download TimeWall for Android with all widgets and dashboard features.'))
  download_features = [
   T('Agenda con un calendario iCal via HTTPS e cache locale.', 'Agenda with one HTTPS iCal calendar and a local cache.'),
   T('Orologio configurabile, due temi e quattro font.', 'Configurable clock, two themes and four fonts.'),
  ] if legacy_download else [
   T('Agenda con un massimo di 20 calendari iCal via HTTPS e cache locale.', 'Agenda with up to 20 HTTPS iCal calendars and a local cache.'),
   T('Meteo, quattro widget e personalizzazione di tema, font e sfondo.', 'Weather, four widgets and customisable themes, fonts and backgrounds.'),
  ]
  if has_backup_and_focus:
   download_features += [
    T('Evento in corso o prossimo di oggi in primo piano, anche nel widget What’s next.', 'Current or next event today in focus, also in the What’s next widget.'),
    T('Backup e ripristino delle impostazioni della dashboard tramite file JSON.', 'Dashboard settings backup and restore via JSON file.'),
    T('Orologio e meteo adatti anche a schermi con meno spazio.', 'Clock and weather adapt to smaller displays.'),
   ]
  else:
   download_features.append(T('Evento in corso o imminente in primo piano.', 'Current or imminent event in focus.'))
  download_features.append(T('Informativa privacy e crediti consultabili nell’app.', 'In-app privacy notice and credits.'))
  feature_items = ''.join(f'<li>{item}</li>' for item in download_features)
  download=f'''<div class="page-intro"><p class="eyebrow">{T("TIMEWALL PER ANDROID","TIMEWALL FOR ANDROID")}</p><h1>{T('La tua giornata<br>ti aspetta.','Your day<br>is waiting.')}</h1><p class="lead">{download_summary}</p></div><div class="download-grid"><article class="download-card primary-card"><span class="tag">{T('DOWNLOAD DIRETTO','DIRECT DOWNLOAD')}</span><h2>TimeWall<span class="brand-dot">.</span> <span class="accent">{release['version']}</span></h2><p>Android 4.4+ · APK · {size} MB</p><a class="button" download href="../downloads/TimeWall-Dashboard.apk">{T('Scarica l’APK','Download APK')}</a><p class="fine">{T('Build','Build')} {release['build']} · {T('APK del','APK dated')} {apk_date}</p><a class="text-link" href="quick-start.html">{T('Come installare e configurare','Installation and setup guide')}</a></article><article class="download-card"><span class="tag muted">{T('PROSSIMAMENTE','COMING SOON')}</span><h2>Google Play</h2><p>{T('TimeWall è in fase di test su Google Play. Qui troverai il collegamento alla scheda pubblica quando sarà disponibile.','TimeWall is being tested on Google Play. The public store listing will be linked here when it becomes available.')}</p><button class="button secondary" disabled>{T('Prossimamente su Google Play','Coming soon to Google Play')}</button></article></div><section class="section changelog"><p class="eyebrow">CHANGELOG</p><h2>{T('Versioni e aggiornamenti','Versions and updates')}</h2><article class="release"><div><h3>{release["version"]}</h3><span class="fine">Build {release["build"]}</span></div><div><h3>TimeWall<span class="brand-dot">.</span></h3><details><summary>{T('Funzioni presenti in questa versione','Features available in this version')}</summary><ul>{feature_items}</ul></details></div></article></section>'''
  info=f'''<div class="page-intro"><p class="eyebrow">{T("IL PROGETTO","THE PROJECT")}</p><h1>{T("Un posto per<br>il tuo tempo.","A place for<br>your time.")}</h1><p class="lead">{T("TimeWall è una dashboard Android da scrivania: mette in evidenza l’evento in corso o il prossimo di oggi e dà un nuovo uso anche ai tablet più datati.","TimeWall is an Android desk dashboard that highlights the current or next event today and gives older tablets a new purpose.")}</p></div><div class="split prose section"><section><h2>{T("Perché TimeWall","Why TimeWall")}</h2><p>{T("L’idea è semplice: dare un utilizzo quotidiano a un tablet, anche datato, rendendo gli impegni facili da consultare. Il supporto parte da Android 4.4 e l’interfaccia è pensata per l’orientamento orizzontale.","The idea is simple: give a tablet, including an older one, an everyday purpose by making plans easy to see. Support starts with Android 4.4 and the interface is designed for landscape orientation.")}</p><h2>{T("Un lettore per i tuoi calendari","A reader for your calendars")}</h2><p>{T("TimeWall supporta calendari iCal pubblici accessibili su HTTPS, indipendentemente dal servizio di provenienza. Non richiede un account TimeWall e non modifica gli eventi presso il fornitore.","TimeWall supports public iCal calendars accessible over HTTPS, regardless of their provider. It requires no TimeWall account and does not edit events at the provider.")}</p></section><section class="author-panel"><img src="../assets/icon.png" width="80" height="80" alt="TimeWall"><h2>Andrea Persano</h2><p>{T("Autore di TimeWall","Creator of TimeWall")}</p><a href="mailto:andreapersano@gmail.com">andreapersano@gmail.com</a><hr><p>{T("Il codice TimeWall è rilasciato con licenza MIT. Le risorse di terze parti mantengono le rispettive licenze.","TimeWall source code is released under the MIT licence. Third-party assets retain their respective licences.")}</p><p><a href="https://github.com/glaciusxp/timewall">{T("Codice sorgente su GitHub","Source code on GitHub")}</a></p><a href="credits.html">{pages['credits']}</a></section></div>'''
  s=strings(lang); sections=[]
  for k in ['privacy_service','privacy_calendars','privacy_weather','privacy_local','privacy_retention','privacy_security','privacy_rights']:
   text=s[k].replace('\\n','\n');title,_,body=text.partition('\n');sections.append(f'<section><h2>{esc(title)}</h2><p>{esc(body)}</p></section>')
  backup_privacy = T(
   'Nelle versioni che consentono il backup manuale, TimeWall salva un file JSON nella destinazione locale che scegli. Il file può includere gli URL privati e i nomi dei calendari, le preferenze meteo e l’immagine di sfondo. Il file è in chiaro e rimane nella destinazione scelta dopo la disinstallazione. Puoi eliminarlo dal gestore file del dispositivo.',
   'In versions with manual backup, TimeWall saves a JSON file to the local destination you choose. This file may include private calendar URLs and names, weather preferences and your background image. The file is unencrypted and stays in the chosen location after uninstalling. You can delete it using your device’s file manager.'
  )
  sections.append(f'<section><h2>{T("Backup delle impostazioni", "Settings backups")}</h2><p>{backup_privacy}</p></section>')
  privacy=f'<div class="page-intro compact"><p class="eyebrow">TIMEWALL</p><h1>{T("Informativa privacy","Privacy notice")}</h1><p class="lead">{T("Titolare: Andrea Persano. Contatto:","Controller: Andrea Persano. Contact:")} <a href="mailto:andreapersano@gmail.com">andreapersano@gmail.com</a></p><p class="fine">{T("Informativa dell’app aggiornata il 26 novembre 2026.","App notice updated on 26 November 2026.")}</p></div><div class="prose legal">'+''.join(sections)+f'<section><h2>{T("Questo sito","This website")}</h2><p>{T("Queste pagine sono statiche: non contengono moduli, pubblicità, analytics o cookie impostati dal codice del sito. Immagini e risorse sono servite dallo stesso sito. Il servizio di hosting può trattare indirizzi IP e dati tecnici necessari a erogare le pagine. Aprire un link esterno comporta l’accesso a un servizio con una propria informativa.","These are static pages: they contain no forms, advertising, analytics or cookies set by the site code. Images and assets are served from the same site. The hosting service may process IP addresses and technical data needed to deliver the pages. Opening an external link takes you to a service with its own privacy notice.")}</p></section><p><a href="https://open-meteo.com/en/terms">Open-Meteo — Terms & Privacy</a><br><a href="https://www.garanteprivacy.it/">Garante per la protezione dei dati personali</a></p></div>'
  credits=f'<div class="page-intro compact"><p class="eyebrow">{T("LE PERSONE E LE RISORSE","PEOPLE & RESOURCES")}</p><h1>{pages["credits"]}</h1><p class="lead">{T("I riconoscimenti per ciò che dà forma a TimeWall.","Acknowledgements for the resources that help shape TimeWall.")}</p></div><div class="prose legal"><section><h2>{T("Licenza di TimeWall","TimeWall licence")}</h2><p>{T("Il codice TimeWall di Andrea Persano è rilasciato con licenza MIT.","TimeWall source code by Andrea Persano is released under the MIT licence.")}</p><a href="../assets/timewall-mit.txt">{T("Testo della licenza MIT","MIT licence text")}</a></section><section><h2>{T("Meteo e località","Weather and locations")}</h2><p>{T("Dati meteo forniti da","Weather data provided by")} <a href="https://open-meteo.com/">Open-Meteo</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.<br>{T("Ricerca località: Open-Meteo con dati","Location search: Open-Meteo with data from")} <a href="https://www.geonames.org/">GeoNames</a>.</p></section><section><h2>{T("Icone e altre risorse","Icons and other assets")}</h2><p>{esc(s["original_assets_credit"])}</p><p>{esc(s["interface_icons_credit"])}</p><a href="https://fontawesome.com/license/free">Font Awesome Free Solid 6.7.2 — SIL OFL 1.1</a></section><section><h2>Font</h2><p>{esc(s["font_conversion_notice"])}</p><p>{T("Roboto di sistema è fornito da Android. Di seguito i testi originali delle licenze distribuite con l’app.","System Roboto is provided by Android. Original licence notices distributed with the app are available below.")}</p><ul class="license-list">'+''.join(f'<li><a href="../assets/licenses/{n}">{n}</a></li>' for n in sorted(notices))+f'</ul></section><section><h2>{T("Screenshot","Screenshots")}</h2><p>{T("Catture reali dell’app su tablet, preparate per la presentazione nello store. Eventi, calendari e misure meteo mostrati sono dati dimostrativi.","Actual tablet app captures prepared for the store listing. Displayed events, calendars and weather values are demonstration data.")}</p></section></div>'
  donation_url = (
   'https://www.paypal.com/donate/?business=AYNTA8ZECH4JJ&no_recurring=0'
   '&item_name=Le+app+che+sviluppo+sono+gratuite+e+prive+di+annunci+pubblicitari.'
   '+Supportami+per+manutenerle+e+crearne+di+nuove.+Grazie%E2%9D%A4%EF%B8%8F&currency_code=EUR'
  )
  donate = f"""<section class="page-intro">
  <h1>{pages['donate']}</h1>
  <p class="lead">{T('Le app che creo sono completamente gratuite, open source e prive di annunci pubblicitari.',
                      'The apps I make are completely free, open source and ad-free.')}</p>
  <p class="lead">{T('Se ti piacciono, puoi aiutarmi a tenerle aggiornate e a crearne di nuove.',
                      'If you enjoy using them, you can help me keep them updated and create new ones.')}</p>
  <div class="actions"><a class="button" href="{esc(donation_url)}">{T('Dona con PayPal','Donate with PayPal')}</a></div>
  </section>"""
  for page,content in [('index',home),('quick-start',quick),('download',download),('info',info),('donate',donate),('privacy',privacy),('credits',credits)]:
   other='en' if it else 'it'
   nav=''.join(f'<a href="{link(p)}" '+('aria-current="page" ' if p==page else '')+f'>{pages[p]}</a>' for p in ['index','quick-start','info','donate'])
   footer=''.join(f'<a href="{link(p)}">{pages[p]}</a>' for p in ['quick-start','download','donate','privacy','credits'])
   title='TimeWall — '+(T('La tua giornata, a colpo d’occhio','Your day, at a glance') if page=='index' else pages[page])
   doc=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{T('TimeWall mette in primo piano l’evento in corso o il prossimo di oggi sul tuo tablet Android. Gratuita e open source.','TimeWall highlights the current or next event today on your Android tablet. Free and open source.')}"><meta name="theme-color" content="#101923"><link rel="icon" href="../assets/icon.png"><link rel="alternate" hreflang="{other}" href="../{other}/{page}.html"><link rel="stylesheet" href="../assets/site.css"><script src="../assets/site.js" defer></script></head><body><a class="skip" href="#main">{T('Vai al contenuto','Skip to content')}</a><header class="site-header"><a class="brand" href="index.html"><img src="../assets/icon.png" alt="" width="50" height="50"><span>TimeWall<span class="brand-dot">.</span></span></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu</button><nav id="navigation" aria-label="{T('Navigazione principale','Main navigation')}">{nav}<a class="nav-download" href="download.html" {('aria-current="page"' if page=='download' else '')}>Download</a><div class="languages" aria-label="{T('Lingua','Language')}"><a href="../it/{page}.html" lang="it" aria-label="Italiano" {('aria-current="true"' if it else '')}>IT</a><span>/</span><a href="../en/{page}.html" lang="en" aria-label="English" {('aria-current="true"' if not it else '')}>EN</a></div></nav></header><main id="main">{content}</main><footer><div class="footer-top"><div><a class="brand" href="index.html"><span>TimeWall<span class="brand-dot">.</span></span></a><p>{T('Il tuo tempo, in primo piano.','Your time, in focus.')}</p></div><nav aria-label="Footer">{footer}</nav></div><div class="footer-bottom"><span>© 2026 Andrea Persano</span><a href="mailto:andreapersano@gmail.com">andreapersano@gmail.com</a><span>{T('Pensato per la tua giornata.','Made for your day.')}</span></div></footer><dialog class="lightbox" aria-label="{T('Screenshot ingrandito','Enlarged screenshot')}"><button class="close-lightbox" autofocus>{T('Chiudi','Close')} ×</button><img alt="" width="1920" height="1200"></dialog></body></html>'''
   (d/(page+'.html')).write_text(doc, encoding='utf-8')
 (OUT/'index.html').write_text('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=it/index.html"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TimeWall</title></head><body><a href="it/index.html">Italiano</a> · <a href="en/index.html">English</a></body></html>')


def build():
 # Stage on the same volume so directory replacement uses renames.
 with TemporaryDirectory(prefix='.timewall-build-', dir=ROOT) as temporary:
  temporary = Path(temporary)
  output = temporary / 'output'
  render(output)
  backup_dir = None
  if DIST.exists():
   backup_dir = Path(mkdtemp(prefix='.timewall-previous-', dir=ROOT)).resolve()
   if backup_dir.parent != ROOT or not backup_dir.name.startswith('.timewall-previous-'):
    raise ValueError('Unexpected backup location')
   DIST.rename(backup_dir / 'dist')
  try:
   output.rename(DIST)
  except BaseException:
   if backup_dir is not None:
    try:
     (backup_dir / 'dist').rename(DIST)
    except OSError as restore_error:
     raise RuntimeError(f'Could not restore dist; backup retained at {backup_dir}') from restore_error
    backup_dir.rmdir()
   raise
  if backup_dir is not None:
   shutil.rmtree(backup_dir)
 print('Generated 14 translated pages and language entry page.')

if __name__ == '__main__':
 build()
