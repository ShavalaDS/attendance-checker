const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "Attendance_Checker.html"), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
const matchingCases = JSON.parse(
    fs.readFileSync(path.join(__dirname, "attendance_cases.json"), "utf8")
);
const csvCases = JSON.parse(
    fs.readFileSync(path.join(__dirname, "csv_cases.json"), "utf8")
);

function createElement() {
    return {
        files: [],
        listeners: {},
        style: {},
        classList: { add() {}, remove() {} },
        addEventListener(eventName, callback) {
            this.listeners[eventName] = callback;
        },
        appendChild() {},
        replaceChildren() {},
        click() {},
        textContent: "",
        className: "",
        disabled: false
    };
}

function createBrowserContext() {
    const elements = new Map();
    const document = {
        getElementById(id) {
            if (!elements.has(id)) elements.set(id, createElement());
            return elements.get(id);
        },
        createElement: createElement
    };
    class MockDataTransfer {
        constructor() {
            this.files = [];
            this.items = { add: file => this.files.push(file) };
        }
    }
    const context = vm.createContext({
        document,
        DataTransfer: MockDataTransfer,
        TextEncoder: require("node:util").TextEncoder
    });
    vm.runInContext(script, context);
    return { context, elements };
}

test("browser CSV extraction agrees with shared delimiter and header cases", () => {
    const { context } = createBrowserContext();
    for (const csvCase of csvCases) {
        const participants = context.extractExpectedNames(context.parseCsv(csvCase.participants));
        const attendees = context.extractAttendeeNames(context.parseCsv(csvCase.attendees));
        assert.deepEqual(Array.from(participants), csvCase.expectedNames, csvCase.name);
        assert.deepEqual(Array.from(attendees), csvCase.attendeeNames, csvCase.name);
    }
});

test("browser matching agrees with shared cases", () => {
    const { context } = createBrowserContext();
    for (const matchingCase of matchingCases) {
        const result = context.compareAttendance(
            [...matchingCase.expectedNames].sort(),
            matchingCase.attendeeNames
        );
        const normalized = {
            missing: Array.from(result.missing),
            extras: Array.from(result.extras),
            ambiguities: Array.from(result.ambiguities, ambiguity => ({
                attendeeName: ambiguity.attendeeName,
                matchingParticipants: ambiguity.matchingParticipants,
                candidateCount: ambiguity.candidateCount
            }))
        };
        assert.deepEqual(normalized, matchingCase.expectedResult, matchingCase.name);
    }
});

test("comparison starts only after the user clicks the button", async () => {
    const { elements } = createBrowserContext();
    const participantFile = {
        name: "participants.csv",
        text: async () => "First Name,Last Name\nMario,Rossi\n"
    };
    const attendeeFile = {
        name: "attendees.csv",
        text: async () => "Name (original name)\nMario\n"
    };

    elements.get("participantsFile").files = [participantFile];
    elements.get("participantsFile").listeners.change();
    elements.get("attendeesFile").files = [attendeeFile];
    elements.get("attendeesFile").listeners.change();

    assert.equal(elements.get("compareButton").disabled, false);
    assert.match(elements.get("status").textContent, /Click Check Attendance/);
    assert.equal(elements.get("results").style.display, "none");

    await elements.get("compareButton").listeners.click();

    assert.equal(elements.get("results").style.display, "block");
    assert.match(elements.get("status").textContent, /Check complete/);
});

test("session reports use a local timestamp and follow empty-report rules", () => {
    const { context } = createBrowserContext();
    const date = new Date(2026, 9, 25, 13, 7);

    let reports = context.buildSessionReports(date, [], [], []);
    assert.equal(reports.timestamp, "2026-10-25_13-07");
    assert.equal(reports.files.length, 1);
    assert.equal(reports.files[0].name, "missing_2026-10-25_13-07.txt");
    assert.equal(
        reports.files[0].content,
        "In today's session (2026-10-25 13:07) nobody is missing! Good Job"
    );

    reports = context.buildSessionReports(date, ["giulia bianchi"], ["luca verdi"], [{
        attendeeName: "Mario",
        matchingParticipants: "Mario Bianchi; Mario Rossi",
        candidateCount: 2
    }]);
    assert.deepEqual(Array.from(reports.files, file => file.name), [
        "missing_2026-10-25_13-07.csv",
        "extras_2026-10-25_13-07.csv",
        "ambiguities_2026-10-25_13-07.csv"
    ]);
});

test("ZIP builder creates a readable archive containing the supplied report files", () => {
    const { context } = createBrowserContext();
    const date = new Date(2026, 9, 25, 13, 7);
    const reports = context.buildSessionReports(
        date,
        ["giulia bianchi"],
        ["luca verdi"],
        [{
            attendeeName: "Mario",
            matchingParticipants: "Mario Bianchi; Mario Rossi",
            candidateCount: 2
        }]
    );
    const archive = Buffer.from(context.createZip(reports.files, date));
    const temporaryDirectory = fs.mkdtempSync(path.join(require("node:os").tmpdir(), "attendance-zip-test-"));
    const archivePath = path.join(temporaryDirectory, "reports.zip");
    try {
        fs.writeFileSync(archivePath, archive);
        require("node:child_process").execFileSync("unzip", ["-t", archivePath], { stdio: "pipe" });
        const listing = require("node:child_process").execFileSync("unzip", ["-Z1", archivePath], { encoding: "utf8" });
        assert.match(listing, /missing_2026-10-25_13-07\.csv/);
        assert.match(listing, /extras_2026-10-25_13-07\.csv/);
        assert.match(listing, /ambiguities_2026-10-25_13-07\.csv/);
        const missingReport = require("node:child_process").execFileSync(
            "unzip",
            ["-p", archivePath, "missing_2026-10-25_13-07.csv"],
            { encoding: "utf8" }
        );
        assert.match(missingReport, /Giulia Bianchi/);
    } finally {
        fs.rmSync(temporaryDirectory, { recursive: true, force: true });
    }
});
