<img width="1350" height="608" alt="attendancechecker" src="https://github.com/user-attachments/assets/f36af231-5217-4fba-a08f-cb4b0d6b68e1" />

# 🚀 Attendance Checker — Stop Wasting Hours on Manual Checks

<p align="left">
  <img src="attendancechecker.gif" alt="Demo of the Attendance Checker web interface: dragging two CSV files into the browser and instantly getting a report of missing and extra participants." width="700">
</p>

<p align="left">
  <strong><a href="https://shavalads.github.io/attendance-checker/Attendance_Checker.html">Try it on your browser →</a></strong>
</p>

Ever spent your evening cross-referencing a Zoom export against an official participant list, only to realize you missed three people? We've all been there.

Attendance Checker takes the bulk of the work out of attendance verification in seconds, with **zero friction**. No manual scrolling, no human error — just instant, reliable results.

---

### ⚡ Two Ways to Use It

**Option A: The Web App (Recommended for Trainers)**
No installation. No terminal. No data leaves your computer.
1. 📂 Open the **[Attendance Checker Web App](https://shavalads.github.io/attendance-checker/Attendance_Checker.html)** in your browser.
2. 🖱️ Drag your participant list and Zoom export onto the drop zones.
3. 📋 Click "Check Attendance" to compare the files, then download the ZIP containing the session reports.

**Option B: The CLI (For Developers & Power Users)**
1. 📂 Drop your files in `1_Participants/` and `2_Attendees/`.
2. ▶️ Run `python main.py`.
3. 📋 Find your results in **`3_Missing_and_Extras/`**. Report filenames include the local run timestamp (`YYYY-MM-DD_HH-mm`). Missing is a CSV when participants are confirmed missing, a TXT confirmation when there are no missing participants or unresolved ambiguities, or a header-only CSV when ambiguities remain but no participant is confirmed missing. Extras and Ambiguities CSVs are created only when they contain results.
4. If an input folder contains multiple CSV files, the CLI lists them and asks which one to use.

*Both paths apply the same matching rules and support comma-, semicolon-, and tab-separated CSVs with the same recognized name-column headers.*

---

### 🧠 Smart Logic — What It Does Well

This isn't a dumb comparison. Attendance Checker is explicitly designed to absorb the messy reality of human data:

*   **Case & whitespace** — inconsistent capitalization and hidden spaces are normalized (e.g., `MARIO ROSSI` and `  mario rossi ` are treated as the same).
*   **Punctuation & accents** — dots, hyphens, slashes, and accented characters are removed or flattened (e.g., `Niccolò` → `niccolo`, `mario.rossi` → `mario rossi`).
*   **Single initials** — *"Mario R."* matches *"Mario Rossi"* when another token, such as "Mario", matches too. An initial that only repeats a token already matched does not count as additional evidence.
*   **Compound names (partial)** — *"Giulia Bianchi"* can match *"Giulia Maria Bianchi"* because the shorter name is contained in the longer one.
*   **Token-based similarity** — names are split into words and compared. Stronger matches take precedence over weaker partial matches; equally strong matches to multiple participants are reported as ambiguous.
*   **The "Extras" catch** — people who joined the call but weren't on the official list are flagged separately in the same output, so you never miss them.
*   **Ambiguous names** — if an attendee name equally matches multiple participants, the candidates are listed in the Ambiguities report, not counted as confirmed present. For example, attendee "Mario" matching expected "Mario Rossi" and "Mario Bianchi" is ambiguous. If another attendee name uniquely identifies "Mario Rossi", Rossi is present and Bianchi is missing; the partial-name ambiguity is still reported. A single expected "Mario Rossi" matched by attendee "Mario" is a unique match. The browser ZIP and CLI output folder contain the timestamped Ambiguities CSV when there are ambiguities.

✅ **Preliminary estimate:** Day-to-day use suggests the tool may reduce manual reconciliation work by roughly 90%. This is an early estimate, not yet measured using a formal test set or methodology.

---

### ⚠️ Known Limitations

To keep the matching logic lightweight and easy to audit, we deliberately excluded some advanced matching techniques. The browser interface has no external library dependencies; the CLI requires Pandas. Here is what the current version does **not** handle:

*   **Nicknames** (*"Bob"* vs *"Robert"*, *"Gianni"* vs *"Giovanni"*) — requires a custom dictionary or an external library.
*   **Typos** (*"Mario Rosi"* vs *"Mario Rossi"*) — requires Levenshtein distance or fuzzy string matching.
*   **Multiple initials** (*"M. R."* vs *"Mario Rossi"*) — the current logic only matches a single initial against a longer token.
*   **Non-Latin scripts** (Chinese, Arabic, Cyrillic) — the normalization pipeline strips non-ASCII characters, meaning names in these scripts become empty strings and are ignored.
*   **Particles attached to surnames** (*"DeLuca"* vs *"De Luca"*) — treated as different tokens. Not normalized.

These limitations are intentional trade-offs. The goal was to solve 90% of real-world cases with a transparent, easily understandable matching engine — not to build a full-blown entity resolution system.

---

### 🎨 Design Philosophy — Designing for the Human, Not the Machine

Every decision in this project was made with the **trainer, HR manager, or event organizer** in mind — not the developer.

**1. Descriptive Naming, Not Developer Lingo**
Folders and files are named for what they *do*, not for what they *are*. You won't find `index.html` or `output/` here. Instead, you'll find `Attendance_Checker.html` (the tool) and `3_Missing_and_Extras` (the exact contents of the folder). The interface starts with the file system.

**2. Privacy First, By Design**
Running the logic client-side (in the browser) isn't just a technical choice — it's a design statement. Your participant data never touches a server. Trainers can work with sensitive information without a second thought.

**3. Progressive Disclosure**
The tool offers two paths: a simple, zero-install web app for everyday users, and a CLI for power users. Both are intended to follow the same matching rules, although their separate implementations and CSV import behavior may differ.

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

*   **Fuzzy Matching 2.0** — introduce Levenshtein distance for typos, a lightweight nickname dictionary, and support for multiple initials (e.g., "M. R." vs "Mario Rossi").
*   **Internationalization (i18n)** — the UI is currently in English. Localizing the interface (and generated filenames) will make the tool accessible to non-English-speaking trainers.
*   **Manual Override in the Web UI** — allow users to review and correct fuzzy matches directly in the browser before downloading the report.
*   **The "Zero-Touch" Workflow** — direct API integrations with Zoom and Google Sheets, background execution, and smart notifications only when anomalies are detected.
*   **Automated Reports** — auto-generate PDF attendance certificates for participants who meet predefined criteria.

---

Built with ❤️ by a Product Designer exploring the intersection of Design and AI. If this saved you time, ⭐ the repo and share it with your team!

---

### 🚀 Quick Start (CLI)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the checker
python main.py
