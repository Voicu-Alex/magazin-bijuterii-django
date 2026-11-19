# Voicu Alexandru, grupa 244

## Magazin de Bijuterii

Proiectul este un site comercial pentru un magazin de bijuterii. Site-ul prezinta si vinde bijuterii lucrate manual sau semnate de branduri cunoscute: inele, coliere, cercei, bratari si pandantive din aur, argint si platina, cu sau fara pietre pretioase. Produsele vor putea fi filtrate dupa categorie, material, pret, brand sau tipul pietrei, iar clientii isi vor putea adauga bijuteriile preferate in cosul virtual. Pe langa catalog, site-ul va contine informatii despre istoria magazinului, colectiile sezoniere, showroom-urile fizice si o pagina de contact.

---

## Diagrama bazei de date

*(se insereaza imaginea `diagrama_bd.png`; sursa editabila este `diagrama_bd.drawio`, care se deschide in draw.io)*

Notatie Chen: dreptunghi = entitate, dreptunghi dublu = entitate slaba, elipsa = atribut, elipsa dubla = atribut cu valori multiple, romb = relatie, romb dublu = relatie de identificare. Atributele subliniate sunt chei primare; `nr_vitrina` este cheie partiala (a entitatii slabe).

### Entitati si atribute

**Bijuterie** – produsul vandut.
- `id_bijuterie` (int, cheie primara)
- `nume` (string) – de ex. "Inel Solitaire Aurora"
- `descriere` (text)
- `pret` (float) – pretul in lei
- `material` (enum: aur, aur alb, argint, platina, otel chirurgical, titan)
- `puritate_carate` (int) – de ex. 14, 18, 24 (pentru argint se foloseste 0)
- `greutate_grame` (float)
- `in_stoc` (boolean)
- `data_adaugare` (date) – data la care produsul a aparut in catalog
- `stiluri` (vector de stringuri, atribut cu valori multiple) – de ex. ["clasic", "minimalist", "vintage"]

**Categorie** – modul de categorisire a produselor (inele, coliere, cercei, bratari, pandantive, ceasuri).
- `id_categorie` (int, cheie primara)
- `nume` (string)
- `descriere` (text)
- `culoare` (string) – culoare reprezentativa, folosita in stilizare (de ex. "#c9a227")
- `sigla` (string) – nume de icon FontAwesome sau cale catre o imagine
- `ordine_afisare` (int) – pozitia categoriei in meniu

**Brand** – producatorul bijuteriei.
- `id_brand` (int, cheie primara)
- `nume` (string)
- `tara_origine` (string)
- `an_infiintare` (int)
- `premium` (boolean) – daca brandul face parte din segmentul de lux

**Colectie** – colectiile (de obicei sezoniere) in care sunt lansate bijuteriile.
- `id_colectie` (int, cheie primara)
- `nume` (string)
- `sezon` (enum: primavara, vara, toamna, iarna)
- `data_lansare` (date)
- `editie_limitata` (boolean)

**PiatraPretioasa** – pietrele care pot fi montate in bijuterii.
- `id_piatra` (int, cheie primara)
- `nume` (string) – diamant, rubin, safir, smarald, ametist etc.
- `duritate_mohs` (float)
- `tip` (enum: pretioasa, semipretioasa, sintetica)

**SediuMagazin** – showroom-urile fizice ale firmei.
- `id_sediu` (int, cheie primara)
- `nume` (string)
- `adresa` (string)
- `telefon` (string)
- `data_deschidere` (date)

**Vitrina** (entitate slaba) – vitrinele de expunere dintr-un sediu.
- `nr_vitrina` (int, cheie partiala) – numarul vitrinei in cadrul sediului
- `etaj` (int)
- `iluminata` (boolean) – daca vitrina are iluminare LED proprie

### Relatii

| Relatie | Entitati | Tip | Explicatie |
|---|---|---|---|
| apartine | Categorie – Bijuterie | one-to-many | o categorie contine mai multe bijuterii; o bijuterie apartine unei singure categorii |
| produce | Brand – Bijuterie | one-to-many | un brand produce mai multe bijuterii; o bijuterie are un singur brand |
| include | Colectie – Bijuterie | one-to-many | o colectie include mai multe bijuterii; o bijuterie face parte din cel mult o colectie |
| contine | Bijuterie – PiatraPretioasa | many-to-many | o bijuterie poate avea mai multe tipuri de pietre, iar acelasi tip de piatra apare in multe bijuterii |
| expune | Vitrina – Bijuterie | many-to-many | intr-o vitrina sunt expuse mai multe bijuterii, iar acelasi model poate fi expus in vitrine din mai multe sedii |
| are | SediuMagazin – Vitrina | one-to-many, de identificare | un sediu are mai multe vitrine; fiecare vitrina apartine unui singur sediu |

Tabelele asociative pentru relatiile many-to-many nu apar in diagrama.

### Entitatea slaba

**Vitrina** este entitate slaba pentru ca nu poate exista si nu poate fi identificata fara sediul din care face parte. Numarul vitrinei (`nr_vitrina`) este unic doar in cadrul unui sediu (fiecare showroom are "vitrina 1", "vitrina 2" etc.), deci cheia completa a unei vitrine este perechea (`id_sediu`, `nr_vitrina`). Daca un sediu se inchide, vitrinele lui dispar odata cu el.

### Tipuri de atribute folosite

string, text, int, float, boolean, enum, date si vector (atributul cu valori multiple `stiluri`) – in total 8 tipuri diferite.

### Forma normala 3

- **FN1**: toate atributele sunt atomice, cu exceptia atributului vector `stiluri`, care este abaterea permisa in cerinta.
- **FN2**: toate entitatile au cheie primara formata dintr-un singur atribut (cu exceptia Vitrinei, unde `etaj` si `iluminata` depind de intreaga cheie (`id_sediu`, `nr_vitrina`), nu doar de o parte din ea).
- **FN3**: nu exista dependente tranzitive – informatiile despre categorie, brand, colectie sau sediu sunt pastrate in entitatile proprii, nu repetate in Bijuterie. Nu exista atribute care se pot calcula din altele (de exemplu nu se pastreaza si vechimea brandului pe langa anul infiintarii, nici numarul de produse dintr-o categorie).
- Nu exista relatii one-to-one.

---

## Utilizatori

Diagrama completata (laboratorul 6) pastreaza toate entitatile anterioare ale produselor si adauga entitatile legate de utilizatori, comenzi si angajati. Diagrama initiala ramane in `diagrama_bd.png` / `diagrama_bd.drawio`; cea completa este in `diagrama_bd_completa.png`, cu sursa editabila `diagrama_bd_completa.drawio`.

*(se insereaza imaginea `diagrama_bd_completa.png`)*

Fata de diagrama initiala, la **Bijuterie** atributul `in_stoc (boolean)` a devenit `stoc (int)` (numarul de bucati, folosit pentru marcarea stocului limitat) si `stiluri` a fost redenumit `taguri` (ramane atribut cu valori multiple), asa cum sunt implementate in `models.py`.

### Utilizator

Corespunde modelului de utilizator (extinde `User` din Django). Pe langa campurile implicite `id_utilizator`, `username`, `parola`, `email`, `nume` si `prenume`, am adaugat:
- `telefon` (string) - numarul de telefon folosit pentru confirmarea comenzilor
- `data_nasterii` (date) - folosita pentru validarea varstei minime (18 ani) si pentru oferte aniversare
- `tara` (string) - tara de resedinta
- `newsletter` (boolean) - daca utilizatorul a acceptat sa primeasca oferte pe e-mail
- `data_inregistrarii` (datetime) - momentul crearii contului

Campurile optionale (care pot ramane necompletate la inregistrare) sunt tinute separat, in entitatea **Profil**, legata de Utilizator prin relatia one-to-one `detaliaza`: `judet`, `oras`, `strada`, `cod_postal` (adresa implicita de livrare), `poza` (calea catre imaginea de profil) si `bio` (o scurta descriere). Daca utilizatorul nu completeaza niciun camp de profil, inregistrarea din Profil nu se creeaza.

### Comanda

Entitatea **Comanda** este legata de Utilizator prin relatia one-to-many `plaseaza` (un utilizator poate avea mai multe comenzi, o comanda apartine unui singur utilizator). Campurile comenzii:
- `id_comanda` (int) - cheie primara
- `data_inregistrarii` (datetime) - momentul plasarii comenzii
- `prin_curier` (boolean) - true daca livrarea se face prin curier, false daca se ridica din showroom
- `status` (enum: inregistrata, confirmata, expediata, livrata, anulata) - starea curenta a comenzii
- `adresa_livrare` (string) - adresa la care se livreaza (poate fi diferita de cea din profil)
- `total` (float) - valoarea totala a comenzii, in lei, dupa aplicarea voucherului
- `observatii` (text) - mentiuni ale clientului (de exemplu, mesaj pentru cadou)

Relatia many-to-many `contine_produse` dintre Comanda si Bijuterie (o comanda contine mai multe produse, un produs apare in mai multe comenzi) are atribute proprii, care vor ajunge in tabelul asociativ: `cantitate` (int) - numarul de bucati din produsul respectiv in comanda - si `pret_unitar` (float) - pretul produsului la momentul comenzii (pretul din catalog se poate schimba ulterior).

### Angajat si Departament

**Angajat** este legat one-to-one de Utilizator prin relatia `este` (un angajat este un utilizator cu date suplimentare) si contine doar datele care tin de statutul de angajat: `functie` (string), `salariu` (float), `data_angajarii` (date), `norma` (enum: intreaga, partiala) si `activ` (boolean - daca mai este angajat in prezent).

**Departament** (entitatea din laboratorul 5) are `nume`, `descriere`, `buget` (float) si `email_contact`. Este legat de Angajat prin doua relatii: `lucreaza_in` (one-to-many: un departament are mai multi angajati, un angajat lucreaza intr-un singur departament) si `conduce` (seful departamentului este un angajat; campul poate fi null pana la numirea unui sef).

### Alte entitati legate de utilizator sau comanda

- **Review** - legat de Utilizator (`scrie`, one-to-many) si de Bijuterie (`evalueaza`, one-to-many). Campuri: `nota` (int, 1-5), `comentariu` (text), `data` (datetime), `aprobat` (boolean - review-ul apare pe site doar dupa aprobarea de catre un angajat).
- **Voucher** - legat de Utilizator (`primeste`, one-to-many) si de Comanda (`aplica`: o comanda poate folosi cel mult un voucher, un voucher poate fi folosit intr-o singura comanda, de aceea cardinalitatea 1 spre Voucher). Campuri: `cod` (string unic), `procent_reducere` (int), `data_expirarii` (date), `folosit` (boolean).
- **Retur** - legat de Comanda (`genereaza`, one-to-many: pentru o comanda se pot deschide mai multe cereri de retur, de exemplu pentru produse diferite). Campuri: `motiv` (text), `data_cererii` (datetime), `status` (enum: deschis, aprobat, respins, rambursat), `suma_rambursata` (float).

### Relatii noi

| Relatie | Entitati | Tip |
|---|---|---|
| este | Utilizator - Angajat | one-to-one |
| detaliaza | Utilizator - Profil | one-to-one |
| plaseaza | Utilizator - Comanda | one-to-many |
| primeste | Utilizator - Voucher | one-to-many |
| scrie | Utilizator - Review | one-to-many |
| evalueaza | Bijuterie - Review | one-to-many |
| contine_produse | Comanda - Bijuterie | many-to-many, cu atributele cantitate si pret_unitar |
| aplica | Voucher - Comanda | one-to-one (optional) |
| genereaza | Comanda - Retur | one-to-many |
| lucreaza_in | Departament - Angajat | one-to-many |
| conduce | Angajat - Departament | one-to-one (sef, poate fi null) |
