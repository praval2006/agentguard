import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CorrectionBrief, correctionText } from "./CorrectionBrief";
import { accountReports } from "./accountDemoData";

describe("controlled correction handoff", () => {
  it("retains two contradictions and excludes unsupported evidence", () => {
    render(<CorrectionBrief report={accountReports.AAA} />);
    expect(screen.getByText("2 evidence-backed corrections")).toBeVisible();
    expect(screen.getByLabelText("Not sent for correction")).toHaveTextContent("UNVERIFIED");
    expect(document.querySelectorAll('.correction-item')).toHaveLength(2);
    expect(screen.getByText(/No agent integration/)).toBeVisible();
  });
  it("copies deterministic fixture evidence without invoking an agent", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
    render(<CorrectionBrief report={accountReports.AAA} />);
    fireEvent.click(screen.getByRole("button", {name: "Copy for coding agent"}));
    expect(writeText).toHaveBeenCalledWith(correctionText(accountReports.AAA));
    expect(await screen.findByText("Correction brief copied. No agent was invoked.")).toBeVisible();
  });
  it("offers manual text when clipboard fails", async () => {
    Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText: vi.fn().mockRejectedValue(new Error()) } });
    render(<CorrectionBrief report={accountReports.DDA} />);
    fireEvent.click(screen.getByRole("button", {name: "Copy for coding agent"}));
    expect(await screen.findByText(/Clipboard unavailable/)).toBeVisible();
    expect(document.querySelectorAll('.correction-item')).toHaveLength(0);
  });
  it("preserves all eight selected fixture outcomes", () => {
    for (const report of Object.values(accountReports)) {
      const before = JSON.stringify(report); const text = correctionText(report);
      expect((text.match(/CORRECTION \d/g) || []).length).toBe(report.fail);
      expect(JSON.stringify(report)).toBe(before);
    }
  });
});
