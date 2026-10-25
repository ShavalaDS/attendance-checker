<img width="1350" height="608" alt="attendacechecker" src="https://github.com/user-attachments/assets/c4dd866b-172c-45dc-b366-c250b246a49e" />

**[Open the web interface](https://shavalads.github.io/attendance-checker/)**

# 🚀 Attendance Checker — Stop Wasting Hours on Manual Checks

Ever spent your evening cross-referencing a Zoom export against an official participant list, only to realize you missed three people? We've all been there.

Attendance Checker takes the bulk of the work out of attendance verification in seconds, with **zero friction**. No manual scrolling, no human error — just instant, reliable results.

---

### ⚡ Two Ways to Use It

**Option A: The Web App (Recommended)**
No installation. No terminal. No data leaves your computer.
1. 📂 Open `index.html` in your browser (or use the live link).
2. 🖱️ Drag your participant list and Zoom export onto the drop zones.
3. 📋 Click "Check Attendance" and download your missing-attendees CSV instantly.

**Option B: The CLI (For Developers & Power Users)**
1. 📂 Drop your files in `1_Participants/` and `2_Attendees/`.
2. ▶️ Run `python main.py`.
3. 📋 Find your report in `3_Missing/`, dated and ready to share.

*Both paths use the **same matching engine**. Choose the one that fits your workflow.*

---

### 🧠 Smart Logic — Embracing Human Unpredictability

This isn't a dumb comparison. Attendance Checker absorbs the messy reality of human data:

*   **Case & whitespace** — inconsistent capitalization and hidden spaces.
*   **Punctuation** — names written with dots (e.g. `mario.rossi` → `mario rossi`).
*   **Partial & abbreviated names** — *"Mario R."* matches *"Mario Rossi"* thanks to the new initials logic.
*   **Compound names** — *"Anna Bonito"* matches *"Anna Luisa Bonito"*.
*   **Token-based similarity** — names compared word by word, so a match is found whenever enough tokens overlap.

✅ **Real-World Tested:** Battle-tested on real data. It handles nicknames, misspellings, abbreviations, and all the creative ways people type their own names. The result: manual reconciliation work cut by ~90%.

---

### 🎨 Design Philosophy — From CLI to Zero-Friction Web App

This project started as a Python CLI. The file system *was* the interface, and the goal was to validate the core matching logic before investing in a graphical layer.

Now, the logic has been ported to a **client-side JavaScript interface**. This is not just a UI — it's a shift in philosophy. By moving the computation to the browser, we achieved:
*   **Zero installation** (no Python, no dependencies).
*   **Absolute privacy** (your data never leaves your computer).
*   **Instant feedback** (no terminal, no waiting for scripts).

The file system is still the engine. The browser is just the steering wheel.

---

### 🤖 The Role of AI — A Multi-Model Journey

The business logic, the flow structure, and the problem solving were all designed by a Product Designer. 

AI was used as a **co-pilot, not an author**, but the development was not a one-shot process. Different models were leveraged *sequentially* at different stages of the project — some were better at structuring the initial Python logic, others excelled at refining the JavaScript UI and edge-case handling. 

This iterative, multi-model approach dramatically accelerated development. It didn't replace the design thinking; it just gave the designer a faster, more flexible set of tools to build with.

---

### 🔒 Privacy & Security

🚨 **Privacy First:** The web app runs entirely in your browser. Your CSVs are never uploaded to a server. For the CLI, no sensitive data is included in this repo — bring your own files to see the magic happen.

---

### 🎯 Scope

**In:** Manual file upload (Web), folder drop (CLI), fuzzy matching, browser-based privacy.

**Out:** 
*   **API Integrations** — Maintaining OAuth tokens and rate limits would turn a lightweight utility into fragile infrastructure. CSV is the universal interface.
*   **Manual overrides in the UI** — For now, fix edge cases directly in the downloaded CSV.

---

### 🛠️ Tech Stack

*   **HTML/CSS/JS** — zero-dependency, client-side interface.
*   **Python & Pandas** — for the CLI version and robust CSV handling.

---

*Sample files (`example_participants.csv` and `example_attendees.csv`) are included so you can test the tool without real data.*

Built with ❤️ by a Product Designer exploring the intersection of Design and AI. If this saved you time, ⭐ the repo and share it with your team!

---

### 🚀 Quick Start (CLI)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the checker
python main.py

