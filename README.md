
# pycoComputer IDE

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Pixi](https://img.shields.io/badge/package_manager-pixi-purple.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

A modern, cross-platform IDE and Emulator for the **picoComputer** architecture, developed using Python and PySide6.

This architecture is central to the "Programming 1" curriculum at the School of Electrical Engineering (ETF), University of Belgrade. It simulates a simplified 16-bit computer designed to teach the fundamentals of assembly language, memory management, and processor execution cycles.

## Features

* **Integrated Code Editor:** Syntax highlighting, auto-completion, and line numbering.
* **Visual Debugger:** Step-by-step execution, breakpoints, and variable inspection.
* **Memory Inspector:** View and edit memory contents in real-time (Signed/Unsigned views).
* **Stack Visualizer:** Dedicated view for the Stack Pointer (SP) and stack frames.
* **16-bit Architecture:** Accurate simulation of overflow, signed arithmetic, and memory addressing.
* **Dark Mode:** Built-in "Dracula" inspired theme.

## Installation & Usage

### Method 1: Using Pixi (Recommended)

This project is managed with [Pixi](https://pixi.prefix.dev/latest/), which handles Python versions and dependencies automatically.

#### For Users (Just Running the App)

1. **Clone and Run:**

    ```bash
    git clone https://github.com/GnuPixie/PycoComputer.git
    cd pico-emulator
    pixi run start
    ```

#### For Developers (Setup & Tools)

1. **Initial Setup:**
    Run this once to install development tools and activate automatic code formatting:

    ```bash
    pixi run -e dev setup
    ```

    *Note: This automatically installs a git hook that formats your code every time you commit.*

2. **Build executable:**

    ```bash
    pixi run -e dev build
    ```

3. **Manual Formatting:**

    ```bash
    pixi run -e dev fmt
    ```

### Method 2: Standard Python (pip)

If you prefer not to use Pixi, you can use a standard Python installation (requires Python 3.9+).

1. **Install dependencies:**

    ```bash
    pip install PySide6
    ```

2. **Run the application:**

    ```bash
    python src/main.py
    ```

## Supported Instructions

| Opcode | Syntax | Description |
| :--- | :--- | :--- |
| **MOV** | `MOV Dest, Src` | Move data between memory/constants. |
| **ADD** | `ADD Dest, Src1, Src2` | Arithmetic addition. |
| **SUB** | `SUB Dest, Src1, Src2` | Arithmetic subtraction. |
| **MUL** | `MUL Dest, Src1, Src2` | Multiplication. |
| **DIV** | `DIV Dest, Src1, Src2` | Integer division. |
| **IN** | `IN Addr, Count` | Read input from user. |
| **OUT** | `OUT Addr, Count` | Print value to terminal. |
| **BEQ** | `BEQ Val1, Val2, Label` | Branch if Equal. |
| **BGT** | `BGT Val1, Val2, Label` | Branch if Greater Than. |
| **JSR** | `JSR Label` | Jump to Subroutine (Push PC to Stack). |
| **RTS** | `RTS` | Return from Subroutine (Pop PC from Stack). |
| **STOP** | `STOP` | Halt execution. |

---

## 🇷🇸 pycoComputer IDE (Srpski)

Moderno razvojno okruženje (IDE) i emulator za **picoComputer** arhitekturu, razvijeno u Python-u uz pomoć PySide6 biblioteke.

Ova arhitektura je sastavni deo predmeta "Programiranje 1" na Elektrotehničkom fakultetu (ETF) u Beogradu. Alat simulira pojednostavljeni 16-bitni procesor sa ciljem lakšeg savladavanja asemblerskog jezika, koncepta adresiranja memorije i životnog ciklusa instrukcija.

### Mogućnosti

* **Editor koda:** Podrška za *syntax highlighting* (bojenje sintakse), automoatsko dopunjavanje instrukcija i numeraciju linija.
* **Vizuelni Debager:** Izvršavanje instrukcija korak-po-korak (*step-by-step*), postavljanje tačaka prekida (*breakpoints*) i praćenje vrednosti promenljivih.
* **Inspektor Memorije:** Pregled i direktna izmena sadržaja memorije u realnom vremenu (prikaz označenih i neoznačenih brojeva).
* **Vizuelizacija Steka:** Namenski panel za praćenje vrha steka (SP) i sadržaja stek okvira.
* **16-bitna Arhitektura:** Verno simuliranje aritmetičkog prekoračenja (*overflow*), rada sa označenim brojevima i memorijskog adresiranja.
* **Tamna Tema:** Integrisan moderni "Dracula" vizuelni stil.

### Instalacija i Pokretanje

#### Metod 1: Korišćenje Pixi-ja (Preporučeno)

Ovaj projekat koristi [Pixi](https://pixi.prefix.dev/latest/) za upravljanje zavisnostima i okruženjem. Ovo je najlakši način za pokretanje jer ne zahteva ručnu instalaciju Python-a.

#### Za Korisnike (Samo pokretanje aplikacije)

1. **Klonirajte i pokrenite:**

    ```bash
    git clone https://github.com/GnuPixie/PycoComputer.git
    cd pico-emulator
    pixi run start
    ```

#### Za Programere (Podešavanje i alati)

1. **Inicijalno podešavanje:**
    Pokrenite ovu komandu jednom kako biste instalirali sve alate i aktivirali automatsko formatiranje koda:

    ```bash
    pixi run -e dev setup
    ```

    *Napomena: Ovo automatski instalira git hook koji formatira kod prilikom svakog commit-a.*

2. **Kreiranje izvršnog fajla:**

    ```bash
    pixi run -e dev build
    ```

3. **Ručno formatiranje:**

    ```bash
    pixi run -e dev fmt
    ```

### Metod 2: Standardni Python (pip)

Ukoliko ne želite da koristite Pixi, možete koristiti standardnu Python instalaciju (potreban je Python 3.9+).

1. **Instalirajte biblioteke:**

    ```bash
    pip install PySide6
    ```

2. **Pokrenite aplikaciju:**

    ```bash
    python src/main.py
    ```

### Podržane Instrukcije

| Opkod | Sintaksa | Opis |
| :--- | :--- | :--- |
| **MOV** | `MOV Dest, Src` | Kopiranje podataka (iz memorije ili konstante). |
| **ADD** | `ADD Dest, Src1, Src2` | Aritmetičko sabiranje. |
| **SUB** | `SUB Dest, Src1, Src2` | Aritmetičko oduzimanje. |
| **MUL** | `MUL Dest, Src1, Src2` | Množenje. |
| **DIV** | `DIV Dest, Src1, Src2` | Celobrojno deljenje. |
| **IN** | `IN Addr, Count` | Učitavanje ulaza sa konzole. |
| **OUT** | `OUT Addr, Count` | Ispis vrednosti na izlazni terminal. |
| **BEQ** | `BEQ Val1, Val2, Label` | Uslovno grananje ako su vrednosti jednake. |
| **BGT** | `BGT Val1, Val2, Label` | Uslovno grananje ako je prva vrednost veća. |
| **JSR** | `JSR Label` | Skok u potprogram (Stavlja PC na stek). |
| **RTS** | `RTS` | Povratak iz potprograma (Skida PC sa steka). |
| **STOP** | `STOP` | Zaustavljanje izvršavanja programa. |
