import os
import re
import unicodedata
from datetime import datetime

import pandas as pd


def find_csv_file(folder):
    """
    Finds the first CSV file in the specified folder.
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

    return csv_files[0]


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

    lower_to_actual = {str(column).strip().lower(): column for column in frame.columns}
    columns = set(lower_to_actual)

    if expected_mode:
        preferred_keys = [
            "first name",
            "first_name",
            "last name",
            "last_name",
            "surname",
            "nome",
            "cognome",
            "name",
            "full name",
            "full_name",
            "name and surname",
        ]

        chosen = []
        for key in preferred_keys:
            actual = lower_to_actual.get(key)
            if actual is not None:
                chosen.append(frame[actual])

        if len(chosen) >= 2:
            names = chosen[0].fillna("").astype(str).str.strip() + " " + chosen[1].fillna("").astype(str).str.strip()
            return names.apply(clean_name)

        if chosen:
            return chosen[0].apply(clean_name)

        if len(frame.columns) >= 2:
            first = frame.iloc[:, 0].fillna("").astype(str).str.strip()
            second = frame.iloc[:, 1].fillna("").astype(str).str.strip()
            return (first + " " + second).apply(clean_name)

        return frame.iloc[:, 0].apply(clean_name)

    if "name (original name)" in columns:
        return frame[lower_to_actual["name (original name)"]].apply(clean_name)

    for key in ["name", "full name", "full_name", "nome completo"]:
        actual = lower_to_actual.get(key)
        if actual is not None:
            return frame[actual].apply(clean_name)

    return frame.iloc[:, 0].apply(clean_name)


def names_match(expected, present):
    """
    Advanced name matching logic:
    1. Perfect match or 2+ common tokens.
    2. Subset match (e.g., "Giulia Bianchi" vs "Giulia Maria Bianchi").
    3. Initials match (e.g., "Mario Rossi" vs "Mario R.").
    """
    expected_tokens = set(filter(None, expected.split()))
    present_tokens = set(filter(None, present.split()))

    if not expected_tokens or not present_tokens:
        return False

    common = expected_tokens & present_tokens
    
    # 1. Perfect match or 2+ common tokens
    if len(common) >= 2:
        return True

    # 2. Subset match
    if expected_tokens.issubset(present_tokens) or present_tokens.issubset(expected_tokens):
        return True

    # 3. Initials match
    if len(common) == 1:
        for e_token in expected_tokens:
            for p_token in present_tokens:
                if len(e_token) > 1 and len(p_token) == 1 and e_token.startswith(p_token):
                    return True
                if len(p_token) > 1 and len(e_token) == 1 and p_token.startswith(e_token):
                    return True

    return False


def compare_attendance(expected_names, present_names):
    expected_names = [name for name in expected_names if name]
    present_names = sorted({name for name in present_names if name})
    definitely_present = set()
    ambiguous_expected = set()
    extras = []
    ambiguities = []

    for present in present_names:
        candidates = [
            index
            for index, expected in enumerate(expected_names)
            if names_match(expected, present)
        ]

        if len(candidates) > 1:
            ambiguous_expected.update(candidates)
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
        df_participants = pd.read_csv(file_participants, encoding="utf-8-sig")
        df_attendees = pd.read_csv(file_attendees, encoding="utf-8-sig")

        expected_names = extract_names(df_participants, expected_mode=True)
        present_names = extract_names(df_attendees)

        missing, extras, ambiguities = compare_attendance(
            expected_names, present_names
        )

        # Create the descriptive folder for trainers
        output_dir = "3_Missing_and_Extras"
        os.makedirs(output_dir, exist_ok=True)
        today_date = datetime.now().strftime("%Y-%m-%d")
        ambiguity_file = os.path.join(
            output_dir, f"ambiguities_{today_date}.csv"
        )
        pd.DataFrame(
            ambiguities,
            columns=["Attendee Name", "Matching Participants", "Candidate Count"],
        ).to_csv(ambiguity_file, index=False)
        
        # Save Missing
        if missing:
            df_missing = pd.DataFrame(missing, columns=["Missing Name"])
            df_missing["Missing Name"] = df_missing["Missing Name"].str.title()
            output_file = os.path.join(output_dir, f"missing_{today_date}.csv")
            df_missing.to_csv(output_file, index=False)
            print(f"✅ Found {len(missing)} missing attendees. Saved to {output_file}")
        else:
            if ambiguities:
                print("⚠️ No confirmed missing attendees. Review the ambiguity report.")
            else:
                print("🎉 No missing attendees! Everyone from the list was present.")

        # Save Extras
        if extras:
            df_extras = pd.DataFrame(extras, columns=["Extra Name"])
            df_extras["Extra Name"] = df_extras["Extra Name"].str.title()
            extra_file = os.path.join(output_dir, f"extras_{today_date}.csv")
            df_extras.to_csv(extra_file, index=False)
            print(f"⚠️ Found {len(extras)} extra attendees (not in the list). Saved to {extra_file}")
        else:
            print("✨ No extra attendees.")

        if ambiguities:
            print(
                f"⚠️ Found {len(ambiguities)} ambiguous attendee names. "
                f"Saved to {ambiguity_file}"
            )
        else:
            print(f"✅ No ambiguous attendee names. Saved empty report to {ambiguity_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()