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
    2. Subset match (e.g., "Mario Rossi" vs "Mario Rossi Bianchi").
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

    # 2. Subset match (one list is entirely contained in the other)
    if expected_tokens.issubset(present_tokens) or present_tokens.issubset(expected_tokens):
        return True

    # 3. Initials match (e.g., "Mario Rossi" vs "Mario R.")
    if len(common) == 1:
        for e_token in expected_tokens:
            for p_token in present_tokens:
                # Check if a short token (initial) matches the start of a long token
                if len(e_token) > 1 and len(p_token) == 1 and e_token.startswith(p_token):
                    return True
                if len(p_token) > 1 and len(e_token) == 1 and p_token.startswith(e_token):
                    return True

    return False


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

        set_expected = {name for name in expected_names if name}
        set_present = {name for name in present_names if name}

        missing = []
        for expected in sorted(set_expected):
            found = False
            for present in set_present:
                if names_match(expected, present):
                    found = True
                    break
            if not found:
                missing.append(expected)

        os.makedirs("3_Missing", exist_ok=True)
        today_date = datetime.now().strftime("%Y-%m-%d")
        output_file = os.path.join("3_Missing", f"missing_{today_date}.csv")

        if missing:
            df_missing = pd.DataFrame(missing, columns=["Missing Name"])
            df_missing["Missing Name"] = df_missing["Missing Name"].str.title()
            df_missing.to_csv(output_file, index=False)
            print(f"✅ Check completed! Found {len(missing)} missing attendees.")
            print(f"📁 File saved at: {output_file}")
        else:
            print("🎉 No missing attendees! Everyone was present.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
