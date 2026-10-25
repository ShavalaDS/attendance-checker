import builtins
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from main import compare_attendance, extract_names, find_csv_file, main, read_csv_file


class CompareAttendanceTests(unittest.TestCase):
    def test_shared_csv_import_cases(self):
        cases_path = Path(__file__).with_name("csv_cases.json")
        cases = json.loads(cases_path.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for case_index, case in enumerate(cases):
                with self.subTest(case=case["name"]):
                    participants_file = root / f"participants-{case_index}.csv"
                    attendees_file = root / f"attendees-{case_index}.csv"
                    participants_file.write_text(case["participants"], encoding="utf-8")
                    attendees_file.write_text(case["attendees"], encoding="utf-8")

                    expected = extract_names(
                        read_csv_file(participants_file), expected_mode=True
                    ).tolist()
                    present = extract_names(read_csv_file(attendees_file)).tolist()
                    self.assertEqual(expected, case["expectedNames"])
                    self.assertEqual(present, case["attendeeNames"])

    def test_cli_prompts_when_input_folder_contains_multiple_csv_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "attendees-a.csv").touch()
            (root / "attendees-b.csv").touch()

            with patch.object(builtins, "input", return_value="2"):
                selected = find_csv_file(temporary_directory)

        self.assertEqual(Path(selected).name, "attendees-b.csv")

    def test_shared_matching_cases(self):
        cases_path = Path(__file__).with_name("attendance_cases.json")
        cases = json.loads(cases_path.read_text(encoding="utf-8"))

        for case in cases:
            with self.subTest(case=case["name"]):
                missing, extras, ambiguities = compare_attendance(
                    case["expectedNames"], case["attendeeNames"]
                )
                result = {
                    "missing": missing,
                    "extras": extras,
                    "ambiguities": [
                        {
                            "attendeeName": row["Attendee Name"],
                            "matchingParticipants": row["Matching Participants"],
                            "candidateCount": row["Candidate Count"],
                        }
                        for row in ambiguities
                    ],
                }
                self.assertEqual(result, case["expectedResult"])

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
                "Matching Participants": "Mario Bianchi; Mario Rossi",
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
            self.assertRegex(reports[0].name, r"^ambiguities_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.csv$")
            missing_reports = list((root / "3_Missing_and_Extras").glob("missing_*.csv"))
            self.assertEqual(len(missing_reports), 1)
            self.assertEqual(
                reports[0].name[len("ambiguities_"):],
                missing_reports[0].name[len("missing_"):],
            )
            self.assertEqual(
                missing_reports[0].read_text(encoding="utf-8").strip(),
                "Missing Name",
            )
            self.assertEqual(
                list((root / "3_Missing_and_Extras").glob("missing_*.txt")),
                [],
            )
            report = pd.read_csv(reports[0])
            self.assertEqual(report.loc[0, "Attendee Name"], "Mario")
            self.assertEqual(report.loc[0, "Matching Participants"], "Mario Bianchi; Mario Rossi")
            self.assertEqual(report.loc[0, "Candidate Count"], 2)

    def test_cli_does_not_write_empty_extras_or_ambiguity_reports(self):
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

            output_directory = root / "3_Missing_and_Extras"
            self.assertEqual(list(output_directory.glob("extras_*.csv")), [])
            self.assertEqual(list(output_directory.glob("ambiguities_*.csv")), [])
            missing_reports = list(output_directory.glob("missing_*.txt"))
            self.assertEqual(len(missing_reports), 1)
            self.assertRegex(missing_reports[0].name, r"^missing_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.txt$")
            self.assertRegex(
                missing_reports[0].read_text(encoding="utf-8"),
                r"In today's session \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}\) nobody is missing! Good Job",
            )


if __name__ == "__main__":
    unittest.main()
