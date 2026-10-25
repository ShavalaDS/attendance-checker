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
    const context = vm.createContext({ document, DataTransfer: MockDataTransfer });
    vm.runInContext(script, context);
    return { context, elements };
}

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
