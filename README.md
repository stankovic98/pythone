# Projekt za kolegij napredno programiranje u pythonu

## Uvod
Dobar dan, ja sam Antonio Stankovic I danas cu vam predstaviti mali dio koda koji implementira osnovnu ideju blockchaina. Blockchain je nepromjenjiv, sekvecijalan lanac zapisa zvanih blokovi. Blokovi mogu sadrzavati tranzakcije, datoteke ili bilo koju vrstu podataka koja vam je potrebna. Vazna stvar za blockchain je da su blokovi medusobno povezani hashevima.

Kod se sastoji do dva djela. Prvi je jednostavna implementacija blockchaina koji sluzi za vodenje evidencije o tranzakcijama, a drugi je implementacija endpointova pomocu FLASK-a za komuniciranje izmedju cvorova/racunala koja koriste nasu kriptovalutu.

## Blockchain klasa
Primjer blockchain:
```
block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

## Flask server

* `/mine`
* `/transaction/new`
* `/chain`
* `/nodes/register`
* `/nodes/resolve`


[Prezentacija](https://docs.google.com/presentation/d/1LpVKW3Dh1amAImvgst9HZkBSLKuYuwul1zFLstkI7-4/edit?usp=sharing)