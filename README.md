# MIROKA-EMOTIONS-INTENCTION
 Developing of 6 emotions and 6 intenctions for miroka to interract with humans

## MIROKA INTRO

Questo lavoro di ricerca si occupa di Miroka, un robot umanoide (metà uomo, metà gatto) 
che fornisce assistenza a bambini o anziani, interagendo con loro con diverse
modalità.

Lo scopo di questo progetto è rendere Miroka ancora più interattivo, inserendo i 
"sentimenti" che prova in determinate situazioni, con l'obiettivo di essere più
empatico, più vicino alle persone e alla realtà e anche più comprensibile
(conoscendo le sue emozioni, si potrà interagire meglio con il robot).

Sviluppiamo quindi 6 emozioni: **Felicità**, **Tristezza**, **Rabbia**, **Disgusto**,
**Paura** e **Sorpresa**; e 6 intenzioni: **"Ho visto qualcuno!"**, **"Sono Concentrato!"**,
**"Sto Pensando!"**, **"Non Ho Capito!"**, **"Mi Sto Annoiando!"**, **"Sto Ascoltando!"**.

## LIBRERIE SENTIMENTI
Prima di costruire il codice completo dove il robot restituisce un emozione in base 
a ciò che vede e ciò che sente, bisogna creare una libreria di emozioni, che utilizzano
i joint come braccia, collo e orecchie, espressioni facciali accompagnate dall'eventuale
effetto sonoro.

### Miroka_Boring
Movimenti: collo abbassato, orecchie abbassate
Espressione facciale: YAWN
Effetto sonoro: NEUTRAL_COOING

### Miroka_Disgust
Movimenti: collo abbassato, orecchie storte
Espressione facciale: DISAPPOINTED
Effetto sonoro: TCHIP

### Miroka_Fear
Movimenti: collo abbassato, orecchie abbassate
Espressione facciale: SCARED1
Effetto sonoro: FEAR_BREATH

### Miroka_Focus
Movimenti: collo dritto, orecchie dritte, braccia sui fianchi
Espressione facciale: THOUGHTFULL
Effetto sonoro: --

### Miroka_Happy
Movimenti: collo dritto, orecchie dritte, saluto
Espressione facciale: FRIENDLY_SMILE
Effetto sonoro: HAPPY_COOING

### Miroka_Interrogative
Movimenti: collo inclinato, orecchie storte
Espressione facciale: LOOK_AROUND
Effetto sonoro: INTERROGATIVE_COOING

### Miroka_Listening
Movimenti: collo dritto, orecchie dritte
Espressione facciale: LISTENING
Effetto sonoro: --

### Miroka_Sad
Movimenti: collo abbassato, orecchie abbassate
Espressione facciale: SAD
Effetto sonoro: SADNESS_MOPE

### Miroka_Seeing
Movimenti: collo dritto, orecchie dritte,
Espressione facciale: FRIENDLY_SMILE
Effetto sonoro: INTEREST_OH

### Miroka_Surprise
Movimenti: collo inclinato leggermenti indietro, orecchie dritte
Espressione facciale: ASTONISHED
Effetto sonoro: SURPRISE_SHOUT

### Miroka_Thinking
Movimenti: collo inclinato a lato, orecchie dritte
Espressione facciale: LOOK_UP
Effetto sonoro: --

# MIROKA EMOTIONS AND INTENTION

Una volta definite le librerie delle emozioni e delle intenzioni, quest'ultime verranno successivamente utilizzate insieme.
Miroka potrà provare uno di questi sentimenti in base a delle condizioni che riesce a percepire grazie alla sua telecamera
e al riconoscimento vocale.

### MIROKA - FELICE
Miroka prova felicità vede qualcuno nel suo campo visivo (utilizzo di telecamera).

### MIROKA - TRISTE
Miroka prova tristezza se, entro 3 secondi, non vede più nessuno (nessuno presente
nel suo campo visivo).

### MIROKA - ARRABBIATO
Tono di voce più alto del normale da parte dell'utente

### MIROKA - DISGUSTATO
*da vedere*

### MIROKA - IMPAURITO
*da vedere*

### MIROKA - SORPRESO
*da vedere*

### MIROKA - HA VISTO QUALCUNO
*da vedere*

### MIROKA - È CONCENTRATO
*da vedere*

### MIROKA - STA PENSANDO
Reazione che potrebbe avere dopo che l'utente ha fatto una domanda al robot

### MIROKA - NON HA CAPITO
Quando la richiesta o la domanda dell'utente non è chiara

### MIROKA - STA ASCOLTANDO
Miroka si mette in ascolto mentre l'utente parla (fa una domanda o chiede di fare qualcosa)

### MIROKA - SI STA ANNOIANDO
Quando Miroka non riceve task o richieste per 10 secondi, si annoia.
