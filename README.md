markdown
Copy
# NOTE THIS PROJECT IS NOT YET AT LARGE (NOT IN USE) HAIJAANZA KUTUMIKA (BADO INATENGENEZWA)
# <img src="docs/logo.svg" width="40"> SPL (Swahili Programming Language)

**Lugha ya Programu Kwa Kiswahili | Version 1.0.0**  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Chaguo la kwanza la programu kwa wanafunzi na wataalam wa Kiswahili!  
*(First-choice programming for Swahili learners and experts!)*

---

## 🚀 Ufungaji wa Haraka (Quick Start)

### **Changanua (Install)**
```bash
git clone https://github.com/JackDonwel/spl.git
cd spl
python -m venv venv
```
```bash
# macOS/Linux
source venv/bin/activate
```
```sh
# Windows
.\venv\Scripts\Activate.ps1
```
```python
pip install -e .
```
```spl
Fanya Mazoezi (Try SPL)

```
```bash
# Anza REPL
python -m src.cli repl
```
```bash
# Tekeleza faili
python -m src.cli run examples/jambo_world.spl
```
🌟 Mfano wa Kodi (Example Code)

examples/jambo_world.spl:
```python


salamu {
    andika("Jambo, Dunia!")  # "Hello, World!" kwa Kiswahili
}
```

🔑 Vipengele Kuu (Key Features)
Kipengele	Maelezo
Syntax ya Kiswahili	Weka funguo maneno kama salamu, andika, na kama badala ya Kiingereza
Mfumo wa Sambamba	zindua funguo-maneno kwa uendeshaji wa sambamba na udhibiti wa mizigo
Aina za Kubuni	Chaguo-msingi aina za kihalisi (nambari, herufi, orodha)
Mazingira Salama	Sanduku-jikoni kwa msimbo usioaminika (hakikisha utekelezaji salama)
Kusanyiko la Papo	Tafsiri kwa LLIM/WebAssembly kupata kasi ya juu
🗺️ Ramani ya Njia (Roadmap)
Awamu ya 1: Msingi wa Lugha (Core Language)

    1.0.0: Tafsiri msingi (andika, kama, shughuli za kihisabati)

    1.1.0: Usaidizi wa safu na fanya kwa vitendo vya kukokotoa

    1.2.0: Ushirikiano na Python kupitia FFI

Awamu ya 2: Zana za Wazoefu (Advanced Tooling)

    2.0.0: Kikokotoo cha REPL chenye msaada wa Kiswahili

    2.1.0: Kiganjo cha Visual Studio Code chenye kusisitiza sintaksia

📚 Maelezo zaidi (Documentation)
Kategoria	Viungo
Syntax	Mwongozo wa Sintaksia
Vipengele vya Kujenga	API ya Msingi
Mafunzo	Mafunzo ya Kuanza
👐 Changia (Contribute)

Tunakaribisha michango yako!
We welcome your contributions!

    Fungua issue kwa mapendekezo yako

    Tembelea Miongozo ya Uchangiaji

    Fanya pull request na mabadiliko yako

```bash
Copy

# Maandalizi ya Maendeleo
git clone https://github.com/JackDonwel/spl.git
python -m pip install -e .[dev]  # Sakinisha vifurushi vya maendeleo
pytest tests/  # Fanya majaribio yote
```
📝 Leseni (License)

Imesimamiwa chini ya MIT License.
📞 Mawasiliano (Contact)

Msimamizi Mkuu: JACK Bombo
Barua pepe: jdonwel@proton.me
Namba ya Simu: +255 785 166 836
Jukwaa: Jiunge na Jukwaa Letu

SPL File Icon
# <img src="docs/logo.svg" width="20">
Faili za .spl zinaonyesha hii ikoni inapounganishwa kikamilifu
