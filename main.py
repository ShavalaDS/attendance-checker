import os
import re
import unicodedata
from datetime import datetime

import pandas as pd


FIRST_NAME_COLUMNS = ["first name", "first_name", "nome"]
LAST_NAME_COLUMNS = ["last name", "last_name", "surname", "cognome"]
FULL_NAME_COLUMNS = [
    "name",
    "full name",
    "full_name",
    "name and surname",
    "nome completo",
]
ATTENDEE_NAME_COLUMNS = ["name (original name)", *FULL_NAME_COLUMNS]


def find_csv_file(folder):
    """
    Finds a CSV file in the specified folder, prompting when there are several.
    """
    if not os.path.exists(folder):
        print(f"Error: Folder '{folder}' does not exist.")
        return None

    csv_files = sorted(
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith(".csv")
    )

    if not csv_files:
        print(f"No CSV file found in '{folder}'.")
        return None

    if len(csv_files) == 1:
        return csv_files[0]

    print(f"Multiple CSV files found in '{folder}':")
    for index, filename in enumerate(csv_files, start=1):
        print(f"  {index}. {os.path.basename(filename)}")

    while True:
        selection = input(f"Choose a file (1-{len(csv_files)}): ").strip()
        try:
            selected_index = int(selection) - 1
        except ValueError:
            print("Enter the number shown next to the file.")
            continue

        if 0 <= selected_index < len(csv_files):
            return csv_files[selected_index]
        print(f"Choose a number between 1 and {len(csv_files)}.")


def detect_csv_delimiter(filename):
    with open(filename, encoding="utf-8-sig", newline="") as csv_file:
        first_line = csv_file.readline()

    delimiters = [",", ";", "\t"]
    return max(delimiters, key=lambda delimiter: first_line.count(delimiter))


def read_csv_file(filename):
    return pd.read_csv(
        filename,
        encoding="utf-8-sig",
        sep=detect_csv_delimiter(filename),
    )


def clean_name(name):
    """
    Normalizes a string by removing accents, punctuation, and extra spaces.
    """
    if pd.isna(name):
        return ""

    text = str(name).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[._/\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_names(frame, expected_mode=False):
    """
    Extracts names from a DataFrame, adapting to different CSV structures.
    """
    if frame is None or frame.empty:
        return []

    lower_to_actual = {
        str(column).strip().lower(): column for column in frame.columns
    }

    if expected_mode:
        first_column = next(
            (lower_to_actual[key] for key in FIRST_NAME_COLUMNS if key in lower_to_actual),
            None,
        )
        last_column = next(
            (lower_to_actual[key] for key in LAST_NAME_COLUMNS if key in lower_to_actual),
            None,
        )
        if first_column is not None and last_column is not None:
            names = (
                frame[first_column].fillna("").astype(str).str.strip()
                + " "
                + frame[last_column].fillna("").astype(str).str.strip()
            )
            return names.apply(clean_name)

        name_columns = FULL_NAME_COLUMNS
    else:
        name_columns = ATTENDEE_NAME_COLUMNS

    for key in name_columns:
        actual = lower_to_actual.get(key)
        if actual is not None:
            return frame[actual].apply(clean_name)

    if expected_mode and len(frame.columns) >= 2:
        first = frame.iloc[:, 0].fillna("").astype(str).str.strip()
        second = frame.iloc[:, 1].fillna("").astype(str).str.strip()
        return (first + " " + second).apply(clean_name)

    return frame.iloc[:, 0].apply(clean_name)


def name_match_score(expected, present):
    expected_tokens = set(filter(None, expected.split()))
    present_tokens = set(filter(None, present.split()))

    if not expected_tokens or not present_tokens:
        return 0

    common = expected_tokens & present_tokens

    if expected_tokens == present_tokens:
        return 1000 + len(common)

    if expected_tokens.issubset(present_tokens) or present_tokens.issubset(expected_tokens):
        return 500 + len(common)

    if len(common) >= 2:
        return 100 + len(common)

    if common:
        for e_token in expected_tokens:
            for p_token in present_tokens:
                if len(e_token) > 1 and len(p_token) == 1 and e_token.startswith(p_token):
                    if common - {e_token}:
                        return 50 + len(common)
                if len(p_token) > 1 and len(e_token) == 1 and p_token.startswith(e_token):
                    if common - {p_token}:
                        return 50 + len(common)

    return 0


def names_match(expected, present):
    return name_match_score(expected, present) > 0


def compare_attendance(expected_names, present_names):
    expected_names = sorted(name for name in expected_names if name)
    present_names = sorted({name for name in present_names if name})
    definitely_present = set()
    ambiguous_candidate_groups = []
    extras = []
    ambiguities = []

    for present in present_names:
        scores = [
            name_match_score(expected, present) for expected in expected_names
        ]
        best_score = max(scores, default=0)
        candidates = [
            index for index, score in enumerate(scores)
            if best_score and score == best_score
        ]

        if len(candidates) > 1:
            ambiguous_candidate_groups.append(set(candidates))
            ambiguities.append({
                "Attendee Name": present.title(),
                "Matching Participants": "; ".join(
                    expected_names[index].title() for index in candidates
                ),
                "Candidate Count": len(candidates),
            })
        elif candidates:
            definitely_present.add(candidates[0])
        else:
            extras.append(present)

    ambiguous_expected = set()
    for candidates in ambiguous_candidate_groups:
        if not candidates & definitely_present:
            ambiguous_expected.update(candidates)

    missing = [
        name
        for index, name in enumerate(expected_names)
        if index not in definitely_present and index not in ambiguous_expected
    ]
    return missing, extras, ambiguities


def main():
    print("Starting attendance check...")
    file_participants = find_csv_file("1_Participants")
    file_attendees = find_csv_file("2_Attendees")

    if not file_participants or not file_attendees:
        return

    try:
        df_participants = read_csv_file(file_participants)
        df_attendees = read_csv_file(file_attendees)

        expected_names = extract_names(df_participants, expected_mode=True)
        present_names = extract_names(df_attendees)

        missing, extras, ambiguities = compare_attendance(
            expected_names, present_names
        )

        # Create the descriptive folder for trainers
        output_dir = "3_Missing_and_Extras"
        os.makedirs(output_dir, exist_ok=True)
        report_time = datetime.now()
        timestamp = report_time.strftime("%Y-%m-%d_%H-%M")
        session_time = report_time.strftime("%Y-%m-%d %H:%M")
        missing_csv = os.path.join(output_dir, f"missing_{timestamp}.csv")
        missing_txt = os.path.join(output_dir, f"missing_{timestamp}.txt")
        extras_file = os.path.join(output_dir, f"extras_{timestamp}.csv")
        ambiguity_file = os.path.join(output_dir, f"ambiguities_{timestamp}.csv")

        for report_path in (missing_csv, missing_txt, extras_file, ambiguity_file):
            if os.path.exists(report_path):
                os.remove(report_path)

        if missing:
            df_missing = pd.DataFrame(missing, columns=["Missing Name"])
            df_missing["Missing Name"] = df_missing["Missing Name"].str.title()
            df_missing.to_csv(missing_csv, index=False)
            print(f"✅ Found {len(missing)} missing attendees. Saved to {missing_csv}")
        elif not ambiguities:
            with open(missing_txt, "w", encoding="utf-8") as report_file:
                report_file.write(
                    f"In today's session ({session_time}) nobody is missing! Good Job"
                )
            print(f"🎉 No missing attendees. Saved confirmation to {missing_txt}")
        else:
            pd.DataFrame(columns=["Missing Name"]).to_csv(missing_csv, index=False)
            print(
                "⚠️ No confirmed missing attendees. Review the ambiguity report. "
                f"Empty missing report saved to {missing_csv}"
            )

        if extras:
            df_extras = pd.DataFrame(extras, columns=["Extra Name"])
            df_extras["Extra Name"] = df_extras["Extra Name"].str.title()
            df_extras.to_csv(extras_file, index=False)
            print(f"⚠️ Found {len(extras)} extra attendees (not in the list). Saved to {extras_file}")
        else:
            print("✨ No extra attendees.")

        if ambiguities:
            pd.DataFrame(
                ambiguities,
                columns=["Attendee Name", "Matching Participants", "Candidate Count"],
            ).to_csv(ambiguity_file, index=False)
            print(f"⚠️ Found {len(ambiguities)} ambiguous attendee names. Saved to {ambiguity_file}")
        else:
            print("✅ No ambiguous attendee names.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()