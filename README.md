# 🚀 Attendance Checker — Stop Wasting Hours on Manual Checks

Ever spent your evening cross-referencing a Zoom export against an official participant list, only to realize you missed three people? We've all been there.

Attendance Checker takes the bulk of the work out of attendance verification in seconds, with **zero friction**. No manual scrolling, no human error — just instant, reliable results.

---

### ⚡ Two Ways to Use It (Choose Your Vibe)

**Option A: The Web App (Recommended for Trainers)**
No installation. No terminal. No data leaves your computer.
1. 📂 Double-click **`Attendance_Checker.html`** — it will open in your default browser.
2. 🖱️ Drag your participant list and Zoom export onto the drop zones.
3. 📋 Click "Check Attendance" and download your report instantly.

**Option B: The CLI (For Developers & Power Users)**
1. 📂 Drop your files in `1_Participants/` and `2_Attendees/`.
2. ▶️ Run `python main.py`.
3. 📋 Find your results in **`3_Missing_and_Extras/`** — you'll get a `missing_YYYY-MM-DD.csv` and an `extras_YYYY-MM-DD.csv`, both dated and ready to share.

*Both paths use the **same matching engine**. Choose the one that fits your workflow.*

---

### 🧠 Smart Logic — Embracing Human Unpredictability

This isn't a dumb comparison. Attendance Checker absorbs the messy reality of human data and the unpredictability of real meetings:

*   **Case & whitespace** — inconsistent capitalization and hidden spaces.
*   **Punctuation** — names written with dots (e.g. `mario.rossi` → `mario rossi`).
*   **Partial & abbreviated names** — *"Mario R."* matches *"Mario Rossi"* thanks to the new initials logic.
*   **Compound names** — *"Anna Bonito"* matches *"Anna Luisa Bonito"*.
*   **Token-based similarity** — names compared word by word, so a match is found whenever enough tokens overlap.
*   **The "Extras" catch** — people who joined the call but weren't on the official list (guests, colleagues dropping by, wrong links) are flagged separately in the same report folder, so you don't miss them.

✅ **Real-World Tested:** Battle-tested on real data. It handles nicknames, misspellings, abbreviations, and all the creative ways people type their own names. The result: manual reconciliation work cut by ~90%.

---

### 🎨 Design Philosophy — Designing for the Human, Not the Machine

Every decision in this project was made with the **trainer, HR manager, or event organizer** in mind — not the developer.

**1. Descriptive Naming, Not Developer Lingo**
Folders and files are named for what they *do*, not for what they *are*. You won't find `index.html` or `output/` here. Instead, you'll find `Attendance_Checker.html` (the tool) and `3_Missing_and_Extras` (the exact contents of the folder). The interface starts with the file system.

**2. Privacy First, By Design**
Running the logic client-side (in the browser) isn't just a technical choice — it's a design statement. Your participant data never touches a server. Trainers can work with sensitive information without a second thought.

**3. Progressive Disclosure**
The tool offers two paths: a simple, zero-install web app for everyday users, and a CLI for power users. Both use the same engine, so the experience is consistent without forcing everyone through the same door.

**4. The "Zero-Touch" Vision**
The current version is intentionally manual: drop two files, get results. But the roadmap is clear — the ultimate goal is a background service that fetches data via APIs, runs the check, and only pings the trainer when something needs their attention. No files, no buttons, no friction.

---

### 🤖 The Role of AI — A Multi-Model Journey

The business logic, the flow structure, and the problem solving were all designed by a Product Designer. 

AI was used as a **co-pilot, not an author**, but the development was not a one-shot process. Different models were leveraged *sequentially* at different stages of the project — some were better at structuring the initial Python logic, others excelled at refining the JavaScript UI and edge-case handling. 

This iterative, multi-model approach dramatically accelerated development. It didn't replace the design thinking; it just gave the designer a faster, more flexible set of tools to build with.

---

### 🔒 Privacy & Security

🚨 **Privacy First:** The web app runs entirely in your browser. Your CSVs are never uploaded to a server. For the CLI, no sensitive data is included in this repo — bring your own files to see the magic happen.

---

### 🛠️ Tech Stack

*   **HTML/CSS/JS** — zero-dependency, client-side interface.
*   **Python & Pandas** — for the CLI version and robust CSV handling.

---

### 🔮 Future Iterations & Scope

*   **UI/UX Refinements in the Web App** — the current interface is a first iteration focused on functional validation. Future updates will focus on improving visual feedback (e.g., loading states, error handling), accessibility, and the overall look and feel to make the browser experience even more seamless and intuitive.
*   **Localization (i18n)** — the UI is currently in English, but the target audience is global. Translating the interface (and the generated filenames) into other languages will make the tool accessible to non-English-speaking trainers. This feature will be prioritized based on user interviews with international training teams.
*   **Manual override in the Web UI** — allow users to correct fuzzy matches on the fly.
*   **The "Zero-Touch" Workflow** — direct API integrations with Zoom and Google Sheets, background execution, and smart notifications only when anomalies are detected.
*   **Automated reports** — auto-generate PDF attendance certificates for those who match the criteria.

---

Built with ❤️ by a Product Designer exploring the intersection of Design and AI. If this saved you time, ⭐ the repo and share it with your team!

---

### 🚀 Quick Start (CLI)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the checker
python main.py

