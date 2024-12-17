# Mesa Bank Reserves Model v Dockeru

Tato dokumentace popisuje, jak spustit příkladový model [Bank Reserves](https://github.com/projectmesa/mesa-examples/tree/main/examples/bank_reserves).

Vysoce abstrahovaný, zjednodušený model ekonomiky s jediným typem agenta a jedinou bankou reprezentující všechny banky v ekonomice. Lidé (reprezentovaní kroužky) se v mřížce pohybují náhodně. Pokud se dva nebo více lidí nachází na stejném místě mřížky, je 50% pravděpodobnost, že spolu budou obchodovat. Pokud obchodují, je stejná šance, že druhému agentovi dají 5 nebo 2 USD. Kladné saldo obchodu se uloží do banky jako úspory. Pokud obchodování vede k zápornému zůstatku, agent se pokusí vybrat ze svých úspor, aby zůstatek pokryl. Pokud nemá dostatek úspor na pokrytí záporného zůstatku, vezme si od banky půjčku na pokrytí rozdílu. Banka je povinna držet určité procento vkladů jako rezervy. 

## 1. Naklonování repozitáře

Nejprve naklonujte repozitář s projektem z GitHubu.
```bash
git clone https://github.com/joachim162/bank_reserves_model
cd Bank-Reserves-model
```

## 2. Příprava prostředí

### Instalace Docker a Docker Compose

Ujistěte se, že máte nainstalovaný Docker a jeho plugin Docker Compose. Pokud nemáte, postupujte podle oficiální dokumentace: 

- [Průvodce pro instalaci Docker](https://docs.docker.com/get-docker/),
- [Průvodce pro instalaci Docker Compose](https://docs.docker.com/compose/install/).

## 3. Spuštění modelu

Spusťte model následujícím příkazem:
```bash
docker-compose up
```

Kontejner automaticky spouští model příkazem `python batch_run.py`. Tímto příkazem je spuštěn model, jehož výstup bude po skončení uložen do `.csv` souboru. Obrázky s vizualizací výstupních dat modelu budou po jeho skončení uloženy do kořenového adresáře repozitáře.

