<img width="1350" height="608" alt="attendacechecker" src="https://github.com/user-attachments/assets/c4dd866b-172c-45dc-b366-c250b246a49e" />

**[Apri l'interfaccia web](https://shavalads.github.io/attendance-checker/)**

# 🚀 Attendance Checker — Stop Wasting Hours on Manual Checks

Ever spent your evening cross-referencing a Zoom export against an official participant list, only to realize you missed three people? We've all been there.

**Attendance Checker** is an MVP that takes the bulk of the work out of attendance verification in seconds, with the least possible friction for the person running it. No more manual scrolling, no more human error — just instant, reliable results.

## ⚡ How It Works (3 Simple Steps)

1. 📂 **Drop your files** — Place your participant list in `1_Participants/` and your Zoom export in `2_Attendees/`.
2. ▶️ **Run the script** — `python main.py`
3. 📋 **Get your report** — Find a neatly formatted CSV of missing attendees in `3_Missing/`, dated and ready to share.

That's it. Zero configuration, zero friction.

## 🎨 Design Philosophy — Why There's No UI

The absence of a UI is a deliberate MVP choice, not a shortcut.

The file system *is* the interface. You simply drag and drop your files into three folders — no buttons, no screens, no learning curve. The goal was to cut the bulk of the work with the minimum possible friction, validating the core logic before investing in a complex graphical interface.

Designing without a UI forced a focus on what actually matters: the reliability of the matching logic, not the chrome around it.

## 🧠 Smart Logic — Embracing Human Unpredictability

This isn't a dumb comparison. Attendance Checker is built to absorb the messy reality of human data:

- **Case & whitespace** — inconsistent capitalization and hidden spaces.
- **Punctuation** — names written with dots (e.g. `mario.rossi` → `mario rossi`).
- **Partial & abbreviated names** — `Mara` matched against `Mara Bruno`.
- **Compound names** — `Anna Bonito` matched against `Anna Luisa Bonito`.
- **Token-based similarity** — names compared word by word, so a match is found whenever enough tokens overlap.

## ✅ Real-World Tested

This tool has already been battle-tested on real data. It has proven capable of handling the unpredictability of actual attendee exports — nicknames, misspellings, abbreviations, and all the creative ways people type their own names. The result: manual reconciliation work cut by roughly 90%.

## 🤖 The Role of AI — Co-pilot, Not Author

The business logic, the flow structure, and the problem solving were all **designed by a Product Designer**. AI (Kilo) was used as a co-pilot to write the Python code — dramatically accelerating development time without replacing design thinking.

## 🔒 Privacy & Security

🚨 **Privacy First:** To protect the innocent (and our colleagues' data), this repo comes with empty folders. Bring your own CSV files to see the magic happen. No sensitive data was harmed in the making of this tool.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the checker
python main.py
```

Place your participant list in `1_Participants/` and your Zoom export in `2_Attendees/`. Your missing-attendees report will appear in `3_Missing/`. Sample files (`example_participants.csv` and `example_attendees.csv`) are included so you can test the tool without real data.

## 🔮 Future Iterations & Scope

Being an MVP, two natural next steps are on the table:

1. **Add a UI** — for users who prefer a graphical interface over folder-based interaction.
2. **Full automation** — direct integration with the Zoom and Google Sheets APIs, eliminating even the manual file download step.

## 🛠️ Tech Stack

- **Python** — clean, readable, and fast.
- **Pandas** — for robust CSV handling and data wrangling.

---

Built with ❤️ by a Product Designer exploring the intersection of Design and AI. If this saved you time, ⭐ the repo and share it with your team!
