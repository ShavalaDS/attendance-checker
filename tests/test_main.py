import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from main import compare_attendance, main


class CompareAttendanceTests(unittest.TestCase):
    def test_single_partial_name_is_confirmed(self):
        missing, extras, ambiguities = compare_attendance(
            ["mario rossi"], ["mario"]
        )

        self.assertEqual(missing, [])
        self.assertEqual(extras, [])
        self.assertEqual(ambiguities, [])

    def test_partial_name_matching_multiple_participants_is_ambiguous(self):
        missing, extras, ambiguities = compare_attendance(
            ["mario rossi", "mario bianchi"], ["mario"]
        )

        self.assertEqual(missing, [])
        self.assertEqual(extras, [])
        self.assertEqual(
            ambiguities,
            [{
                "Attendee Name": "Mario",
                "Matching Participants": "Mario Rossi; Mario Bianchi",
                "Candidate Count": 2,
            }],
        )

    def test_duplicate_full_names_are_preserved_as_ambiguous_candidates(self):
        missing, extras, ambiguities = compare_attendance(
            ["mario rossi", "mario rossi"], ["mario rossi"]
        )

        self.assertEqual(missing, [])
        self.assertEqual(extras, [])
        self.assertEqual(ambiguities[0]["Candidate Count"], 2)
        self.assertEqual(
            ambiguities[0]["Matching Participants"],
            "Mario Rossi; Mario Rossi",
        )

    def test_definite_match_and_extra_are_kept_separate(self):
        missing, extras, ambiguities = compare_attendance(
            ["mario rossi", "giulia bianchi"],
            ["mario rossi", "luca verdi"],
        )

        self.assertEqual(missing, ["giulia bianchi"])
        self.assertEqual(extras, ["luca verdi"])
        self.assertEqual(ambiguities, [])

    def test_cli_writes_ambiguity_report_in_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "1_Participants").mkdir()
            (root / "2_Attendees").mkdir()
            pd.DataFrame({
                "Nome": ["Mario", "Mario"],
                "Cognome": ["Rossi", "Bianchi"],
            }).to_csv(root / "1_Participants" / "participants.csv", index=False)
            pd.DataFrame({
                "Name (original name)": ["Mario"],
            }).to_csv(root / "2_Attendees" / "attendees.csv", index=False)

            original_directory = os.getcwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(io.StringIO()):
                    main()
            finally:
                os.chdir(original_directory)

            reports = list((root / "3_Missing_and_Extras").glob("ambiguities_*.csv"))
            self.assertEqual(len(reports), 1)
            report = pd.read_csv(reports[0])
            self.assertEqual(report.loc[0, "Attendee Name"], "Mario")
            self.assertEqual(report.loc[0, "Matching Participants"], "Mario Rossi; Mario Bianchi")
            self.assertEqual(report.loc[0, "Candidate Count"], 2)

    def test_cli_writes_header_only_when_no_ambiguities_exist(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "1_Participants").mkdir()
            (root / "2_Attendees").mkdir()
            pd.DataFrame({
                "Nome": ["Mario"],
                "Cognome": ["Rossi"],
            }).to_csv(root / "1_Participants" / "participants.csv", index=False)
            pd.DataFrame({
                "Name (original name)": ["Mario"],
            }).to_csv(root / "2_Attendees" / "attendees.csv", index=False)

            original_directory = os.getcwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(io.StringIO()):
                    main()
            finally:
                os.chdir(original_directory)

            reports = list((root / "3_Missing_and_Extras").glob("ambiguities_*.csv"))
            self.assertEqual(len(reports), 1)
            self.assertEqual(
                reports[0].read_text(encoding="utf-8").strip(),
                "Attendee Name,Matching Participants,Candidate Count",
            )


if __name__ == "__main__":
    unittest.main()
