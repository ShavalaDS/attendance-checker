import pandas as pd
import os
from datetime import datetime

def find_csv_file(folder):
    if not os.path.exists(folder):
        print(f"Error: Folder '{folder}' does not exist.")
        return None
    for file in os.listdir(folder):
        if file.endswith('.csv'):
            return os.path.join(folder, file)
    print(f"No CSV file found in '{folder}'.")
    return None

def clean_name(name):
    if pd.isna(name): return ""
    # Pulisce il nome: minuscolo, sostituisce i punti con spazi e toglie spazi doppi
    return str(name).strip().lower().replace('.', ' ').replace("  ", " ")

def main():
    print("Starting attendance check...")
    file_participants = find_csv_file("1_Participants")
    file_attendees = find_csv_file("2_Attendees")
    
    if not file_participants or not file_attendees:
        return

    try:
        df_participants = pd.read_csv(file_participants)
        df_attendees = pd.read_csv(file_attendees)
        
        # LEGGI IL FILE DEI PARTECIPANTI (Google Sheets)
        expected_names = df_participants.iloc[:, 0].astype(str) + " " + df_participants.iloc[:, 1].astype(str)
            
        # LEGGI IL FILE DEI PRESENTI (Zoom)
        if 'Name (original name)' in df_attendees.columns:
            present_names = df_attendees['Name (original name)']
        else:
            present_names = df_attendees.iloc[:, 0]

        # Applica la pulizia
        set_expected = set(expected_names.apply(clean_name))
        set_present = set(present_names.apply(clean_name))
        
        if "" in set_expected: set_expected.remove("")
        if "" in set_present: set_present.remove("")

        # Trova i mancanti con matching basato su token
        missing = []
        for expected in set_expected:
            expected_tokens = expected.split()
            found = False
            for present in set_present:
                present_tokens = present.split()
                common = len(set(expected_tokens) & set(present_tokens))
                if common >= 2 or all(tok in expected_tokens for tok in present_tokens):
                    found = True
                    break
            if not found:
                missing.append(expected)
        
        # Salva il file finale
        today_date = datetime.now().strftime("%Y-%m-%d")
        output_file = f"3_Missing/missing_{today_date}.csv"
        
        if missing:
            df_missing = pd.DataFrame(list(missing), columns=["Missing Name"])
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