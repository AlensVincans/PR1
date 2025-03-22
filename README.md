# Spēle - Akmentiņu stratēģija

## Apraksts
Šī ir stratēģiska spēle, kurā divi spēlētāji sacenšas, pēc kārtas ņemot akmentiņus no galda un ievērojot noteiktus punktu piešķiršanas mehānismus. Viens no spēlētājiem ir cilvēks, bet otrs – dators, kurš izmanto Minimaksa vai Alfa-beta algoritmu, lai pieņemtu lēmumus.

## Funkcionalitāte
Programmatūra nodrošina šādas iespējas:
- Izvēlēties, kurš uzsāk spēli: cilvēks vai dators.
- Izvēlēties datora algoritmu: Minimaksa vai Alfa-beta algoritmu.
- Veikt gājienus un redzēt izmaiņas spēles laukumā.
- Uzsākt spēli atkārtoti pēc tās pabeigšanas.
- Grafisko lietotāja saskarni ar pygame.

## Spēles noteikumi
1. Spēle sākas ar 50 līdz 70 akmentiņiem, ko izvēlas spēlētājs.
2. Katrs spēlētājs sāk ar 0 punktiem un 0 akmentiņiem.
3. Spēlētāji pēc kārtas paņem 2 vai 3 akmentiņus.
4. Ja pēc gājiena uz galda paliek pāra skaits, pretinieks saņem 2 punktus.
5. Ja pēc gājiena uz galda paliek nepāra skaits, spēlētājs saņem 2 punktus.
6. Spēle beidzas, kad uz galda nav akmentiņu.
7. Spēlētājiem piešķir papildu punktus par saviem savāktajiem akmentiņiem.
8. Uzvar spēlētājs ar lielāko punktu skaitu, ja punktu skaits vienāds – neizšķirts.

## Tehniskās prasības
- **Programmas valoda:** Python
- **Bibliotēkas:** `pygame`
- **Git repozitorijs:** [PR1](https://github.com/AlensVincans/PR1)

## Algoritmi un Eksperimenti
- Spēles koka veidošana datu struktūras veidā (klases, saistītie saraksti).
- Heiristiskās novērtējuma funkcijas izstrāde.
- Minimaksa un Alfa-beta algoritmu realizācija ar n-gājienu pārlūkošanu.
- 10 eksperimenti ar katru algoritmu:
  - Uzvaru skaits (cilvēks vs. dators)
  - Datora apmeklēto virsotņu skaits
  - Vidējais gājiena izpildes laiks

## Instalācija un Palaišana
1. Klonējiet repozitoriju:
   ```sh
   git clone https://github.com/AlensVincans/PR1.git
   ```
2. Instalējiet nepieciešamās bibliotēkas:
   ```sh
   pip install pygame
   ```
3. Palaižiet spēli:
   ```sh
   python main.py
   ```

## Izstrādātāji
- **Aleksandrs Belkins**
- **Ksenija Šitikova**
- **Alens Vincāns**
- **Marks Šafirs**
- **Roberts Ozoliņš**
