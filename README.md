# AltPlan

[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/GrzybowskiBYD/AltPlan/blob/main/README.en.md)
[![pl](https://img.shields.io/badge/lang-pl-red.svg)](https://github.com/GrzybowskiBYD/AltPlan/blob/main/README.md)

Altplan to program, który interpretuje dane z planu lekcji, a następnie przedstawia je w przystępnej formie na stronie internetowej.

---
Altplan został stworzony z myślą o uczniach oraz nauczycielach, którzy na co dzień korzystają z oryginalnej — nieczytelnej i ubogiej w funkcje — [strony planu lekcji](https://plan.zse.bydgoszcz.pl).

Altplan wprowadza wiele udogodnień i funkcji m.in.:
1. Nanoszenie zastępstw na plan
2. Ciemny motyw oraz wybór koloru motywu
3. Dedykowaną wersję mobilną
4. Godzinę ostatniej aktualizacji
5. Pole Szczęśliwego Numerka
6. Wiele innych drobnych poprawek

Gotową stronę można zobaczyć na stronie [altplan.zse.bydgoszcz.pl](https://altplan.zse.bydgoszcz.pl).

## Instalacja

Aby zainstalować Altplan, należy:
1. Upewnić się, że Docker jest zainstalowany 
2. (Opcjonalnie) utworzyć fork'a repozytorium
3. Sklonować repozytorium
4. Użyć polecenia `docker compose -f .\docker-compose.yml up` lub zastosować się do [dokumentacji](https://docs.docker.com/reference/cli/docker/compose/#examples)
5. Gotowe! Altplan powinien być dostępny pod adresem [localhost:80](http://localhost:80)