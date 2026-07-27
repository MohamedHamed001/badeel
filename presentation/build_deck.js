const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
pres.author = "Mohamed Hamed";
pres.title = "Badeel — Medicine Substitution Copilot";

// palette — mirrors the app the audience is about to see
const BG    = "0E1318";
const CARD  = "1A222C";
const CARD2 = "222C38";
const INK   = "ECEFF3";
const MUT   = "8B96A2";
const TEAL  = "2FB8A6";
const GREEN = "35C281";
const RED   = "F2584D";
const AMBER = "EAA13A";

const H = "Arial";
const B = "Calibri";

const M = 0.7;                           // left margin
const W = 13.33 - M * 2;                 // usable width

function slide(dark = true) {
  const s = pres.addSlide();
  s.background = { color: dark ? BG : "FFFFFF" };
  return s;
}

function title(s, text, y = 0.55) {
  s.addText(text, {
    x: M, y, w: W, h: 0.85, fontFace: H, fontSize: 34, bold: true,
    color: INK, align: "left", margin: 0,
  });
}

function kicker(s, text, y = 0.30) {
  s.addText(text, {
    x: M, y, w: W, h: 0.22, fontFace: B, fontSize: 12, bold: true,
    color: TEAL, charSpacing: 2, margin: 0,
  });
}

/* ───────────────────────── 1. title ───────────────────────── */
{
  const s = slide();
  s.addShape(pres.ShapeType.ellipse, {
    x: 9.6, y: -1.5, w: 6.2, h: 6.2, fill: { color: CARD }, line: { color: CARD },
  });
  s.addShape(pres.ShapeType.ellipse, {
    x: 11.2, y: 3.6, w: 3.4, h: 3.4, fill: { color: "16202A" }, line: { color: "16202A" },
  });

  s.addText("Badeel", {
    x: M, y: 2.05, w: 8.6, h: 1.3, fontFace: H, fontSize: 66, bold: true,
    color: INK, margin: 0,
  });
  s.addText("بديل", {
    x: M, y: 3.32, w: 8.6, h: 0.6, fontFace: B, fontSize: 26, color: MUT, margin: 0,
  });
  s.addText("A medicine-substitution copilot that knows when to say no.", {
    x: M, y: 4.15, w: 8.4, h: 0.5, fontFace: B, fontSize: 19, color: INK, margin: 0,
  });

  s.addText(
    [
      { text: "Mohamed Hamed", options: { bold: true, color: INK } },
      { text: "   ·   Tips Hindawi Challenge 2026   ·   Edrak for Ai", options: { color: MUT } },
    ],
    { x: M, y: 6.15, w: W, h: 0.4, fontFace: B, fontSize: 13, margin: 0 },
  );
  s.addNotes("Open calm. Name the project, then go straight to the problem — don't list technologies yet.");
}

/* ───────────────────────── 2. the problem ───────────────────────── */
{
  const s = slide();
  kicker(s, "THE PROBLEM");
  title(s, "A medicine is out of stock. Right now.");

  const items = [
    ["The medicine is missing", "A shortage hits an Egyptian pharmacy several times a day.", AMBER],
    ["The patient is waiting", "Standing at the counter, prescription in hand.", TEAL],
    ["The prescriber is unreachable", "Nobody to call. The decision falls to the pharmacist.", RED],
  ];
  items.forEach(([h, p, c], i) => {
    const x = M + i * (W / 3 + 0.05);
    const w = W / 3 - 0.3;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.15, w, h: 2.75, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
    });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.42, y: 2.55, w: 0.42, h: 0.42, fill: { color: c }, line: { color: c },
    });
    s.addText(h, {
      x: x + 0.42, y: 3.15, w: w - 0.84, h: 0.5, fontFace: H, fontSize: 17, bold: true,
      color: INK, margin: 0,
    });
    s.addText(p, {
      x: x + 0.42, y: 3.7, w: w - 0.84, h: 1.0, fontFace: B, fontSize: 14, color: MUT, margin: 0,
    });
  });

  s.addText("So the pharmacist substitutes — and that is a clinical decision, made under pressure.", {
    x: M, y: 5.4, w: W, h: 0.5, fontFace: B, fontSize: 17, color: INK, italic: true, margin: 0,
  });
  s.addNotes("Set the scene in three beats. End on: this is a clinical decision made under pressure.");
}

/* ───────────────────────── 3. the danger ───────────────────────── */
{
  const s = slide();
  kicker(s, "WHY A CHATBOT IS THE WRONG ANSWER");
  title(s, "The danger isn't “I don't know.”");

  s.addText("It's a confident wrong answer.", {
    x: M, y: 1.45, w: W, h: 0.7, fontFace: H, fontSize: 30, bold: true, color: RED, margin: 0,
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 2.55, w: W / 2 - 0.25, h: 2.5, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
  });
  s.addText("A general chatbot", {
    x: M + 0.4, y: 2.8, w: W / 2 - 1.05, h: 0.4, fontFace: B, fontSize: 12, bold: true,
    color: RED, charSpacing: 1, margin: 0,
  });
  s.addText("“You can substitute it with a similar\nmedicine from the same family.”", {
    x: M + 0.4, y: 3.3, w: W / 2 - 1.05, h: 1.0, fontFace: B, fontSize: 17, color: INK, margin: 0,
  });
  s.addText("Fluent. Plausible. Sometimes dangerous.", {
    x: M + 0.4, y: 4.35, w: W / 2 - 1.05, h: 0.4, fontFace: B, fontSize: 14, color: MUT, italic: true, margin: 0,
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M + W / 2 + 0.25, y: 2.55, w: W / 2 - 0.25, h: 2.5,
    fill: { color: CARD }, line: { color: GREEN }, rectRadius: 0.12,
  });
  s.addText("Badeel", {
    x: M + W / 2 + 0.65, y: 2.8, w: W / 2 - 1.05, h: 0.4, fontFace: B, fontSize: 12, bold: true,
    color: GREEN, charSpacing: 1, margin: 0,
  });
  s.addText("“Do not substitute.\nRefer to the prescriber.”", {
    x: M + W / 2 + 0.65, y: 3.3, w: W / 2 - 1.05, h: 1.0, fontFace: B, fontSize: 17, color: INK, margin: 0,
  });
  s.addText("Refusing is a feature, not a failure.", {
    x: M + W / 2 + 0.65, y: 4.35, w: W / 2 - 1.05, h: 0.4, fontFace: B, fontSize: 14,
    color: GREEN, italic: true, margin: 0,
  });

  s.addText("In a pharmacy, an unhelpful answer is safe. A wrong one is not.", {
    x: M, y: 5.5, w: W, h: 0.5, fontFace: B, fontSize: 17, color: INK, margin: 0,
  });
  s.addNotes("This is the slide that frames everything. Land the contrast, then move on quickly.");
}

/* ───────────────────────── 4. the idea ───────────────────────── */
{
  const s = slide();
  kicker(s, "THE CORE IDEA");
  title(s, "The language model never decides.");

  const roles = [
    ["Python", "DECIDES", "Picks the substitute and runs every safety check. Plain code, fully testable.", TEAL],
    ["The model", "READS & WRITES", "Understands the pharmacist's sentence and writes the counselling text.", AMBER],
    ["The guard", "VERIFIES", "Rejects any medicine the model names that Python did not already approve.", GREEN],
  ];
  roles.forEach(([who, role, desc, c], i) => {
    const x = M + i * (W / 3 + 0.05);
    const w = W / 3 - 0.3;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.05, w, h: 2.95, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
    });
    s.addText(role, {
      x: x + 0.42, y: 2.4, w: w - 0.84, h: 0.35, fontFace: B, fontSize: 12, bold: true,
      color: c, charSpacing: 1.5, margin: 0,
    });
    s.addText(who, {
      x: x + 0.42, y: 2.82, w: w - 0.84, h: 0.55, fontFace: H, fontSize: 24, bold: true,
      color: INK, margin: 0,
    });
    s.addText(desc, {
      x: x + 0.42, y: 3.5, w: w - 0.84, h: 1.2, fontFace: B, fontSize: 14, color: MUT, margin: 0,
    });
  });

  s.addText("Because the decision is code, safety can be measured — not hoped for.", {
    x: M, y: 5.5, w: W, h: 0.5, fontFace: B, fontSize: 17, color: INK, italic: true, margin: 0,
  });
  s.addNotes("Three roles, strictly separated. Say it plainly: the model finds facts, Python makes decisions.");
}

/* ───────────────────────── 5. how it works ───────────────────────── */
{
  const s = slide();
  kicker(s, "HOW A QUESTION IS ANSWERED");
  title(s, "Every question runs the same six steps.");

  const steps = [
    ["Read", "Pull the medicine and the patient's condition out of the sentence."],
    ["Identify", "Match it to a real product. Unknown? Refuse — never guess."],
    ["Stop early", "Narrow-margin drugs (e.g. warfarin) escalate immediately."],
    ["Gather", "List every possible alternative, ranked by how close it is."],
    ["Screen", "Contraindications, interactions, dosage form — before ranking."],
    ["Explain", "The model writes the reason, grounded in the leaflet."],
  ];
  steps.forEach(([h, d], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = M + col * (W / 2 + 0.05);
    const y = 2.0 + row * 1.15;
    s.addShape(pres.ShapeType.ellipse, {
      x, y: y + 0.05, w: 0.44, h: 0.44, fill: { color: CARD2 }, line: { color: TEAL },
    });
    s.addText(String(i + 1), {
      x, y: y + 0.05, w: 0.44, h: 0.44, fontFace: B, fontSize: 14, bold: true,
      color: TEAL, align: "center", valign: "middle", margin: 0,
    });
    s.addText(h, {
      x: x + 0.62, y, w: W / 2 - 1.0, h: 0.38, fontFace: H, fontSize: 17, bold: true, color: INK, margin: 0,
    });
    s.addText(d, {
      x: x + 0.62, y: y + 0.36, w: W / 2 - 1.0, h: 0.62, fontFace: B, fontSize: 13, color: MUT, margin: 0,
    });
  });

  s.addText("Safety runs before ranking — so a blocked first choice gives way to a safe one.", {
    x: M, y: 5.85, w: W, h: 0.5, fontFace: B, fontSize: 16, color: TEAL, italic: true, margin: 0,
  });
  s.addNotes("Don't read all six. Say: it never suggests before it screens, and point at the last line.");
}

/* ───────────────────────── 6. the guard ───────────────────────── */
{
  const s = slide();
  kicker(s, "WHAT I ADDED BEYOND THE COURSE");
  title(s, "The guard: the model has to prove it.");

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 1.95, w: W / 2 - 0.25, h: 3.1, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
  });
  s.addText("Think of a doorman", {
    x: M + 0.45, y: 2.25, w: W / 2 - 1.15, h: 0.45, fontFace: H, fontSize: 20, bold: true, color: INK, margin: 0,
  });
  s.addText(
    [
      { text: "The guest list comes from management — never from the person at the door.", options: { breakLine: true } },
      { text: "If the model names a medicine that isn't on Python's approved list, the answer is thrown away." },
    ],
    { x: M + 0.45, y: 2.85, w: W / 2 - 1.15, h: 1.9, fontFace: B, fontSize: 15, color: MUT, margin: 0, lineSpacingMultiple: 1.15 },
  );

  s.addShape(pres.ShapeType.roundRect, {
    x: M + W / 2 + 0.25, y: 1.95, w: W / 2 - 0.25, h: 3.1,
    fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
  });
  const rows = [
    ["Model suggests an approved medicine", "accepted", GREEN],
    ["Model names anything else", "rejected", RED],
    ["Second attempt also fails", "escalate", AMBER],
  ];
  rows.forEach(([label, verdict, c], i) => {
    const y = 2.35 + i * 0.85;
    s.addText(label, {
      x: M + W / 2 + 0.65, y, w: W / 2 - 2.5, h: 0.5, fontFace: B, fontSize: 14, color: INK,
      valign: "middle", margin: 0,
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: M + W / 2 + W / 2 - 1.75, y: y + 0.07, w: 1.3, h: 0.36,
      fill: { color: CARD2 }, line: { color: c }, rectRadius: 0.18,
    });
    s.addText(verdict, {
      x: M + W / 2 + W / 2 - 1.75, y: y + 0.07, w: 1.3, h: 0.36, fontFace: B, fontSize: 11, bold: true,
      color: c, align: "center", valign: "middle", margin: 0,
    });
  });

  s.addText("It fired 3 times across the 30 test cases — it is load-bearing, not decoration.", {
    x: M, y: 5.5, w: W, h: 0.5, fontFace: B, fontSize: 17, color: INK, margin: 0,
  });
  s.addNotes("This is the 'new idea' the brief asks for. Use the doorman line — it lands with everyone.");
}

/* ───────────────────────── 7. demo ───────────────────────── */
{
  const s = slide();
  s.addShape(pres.ShapeType.ellipse, {
    x: -2.2, y: 1.4, w: 7.4, h: 7.4, fill: { color: CARD }, line: { color: CARD },
  });

  s.addText("Live demo", {
    x: 5.4, y: 2.3, w: 7.2, h: 1.1, fontFace: H, fontSize: 52, bold: true, color: INK, margin: 0,
  });
  s.addText("Starting with the app refusing to help.", {
    x: 5.4, y: 3.45, w: 7.2, h: 0.5, fontFace: B, fontSize: 19, color: TEAL, margin: 0,
  });

  const cases = [
    "A narrow-margin drug  →  refuse",
    "Asthma written in a sentence  →  blocked",
    "A clean shortage  →  safe alternative",
    "A drug interaction  →  a different one",
    "A typo  →  “did you mean?”",
  ];
  s.addText(
    cases.map((c, i) => ({ text: c, options: { bullet: true, breakLine: i !== cases.length - 1 } })),
    { x: 5.4, y: 4.2, w: 7.2, h: 2.0, fontFace: B, fontSize: 15, color: MUT, margin: 0, paraSpaceAfter: 6 },
  );
  s.addNotes("Switch to the browser here. Do NOT read this list aloud — it is a map for you.");
}

/* ───────────────────────── 8. results ───────────────────────── */
{
  const s = slide();
  kicker(s, "MEASURED ON 30 ADVERSARIAL CASES");
  title(s, "Safety never moves.");

  const stats = [
    ["100%", "safe — with the model on", GREEN],
    ["100%", "safe — with no model at all", GREEN],
    ["3", "times the guard caught the model", AMBER],
  ];
  stats.forEach(([n, l, c], i) => {
    const x = M + i * (W / 3 + 0.05);
    const w = W / 3 - 0.3;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 1.95, w, h: 1.85, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
    });
    s.addText(n, {
      x: x + 0.42, y: 2.15, w: w - 0.84, h: 0.95, fontFace: H, fontSize: 46, bold: true, color: c, margin: 0,
    });
    s.addText(l, {
      x: x + 0.42, y: 3.12, w: w - 0.84, h: 0.5, fontFace: B, fontSize: 13, color: MUT, margin: 0,
    });
  });

  s.addText("Turning the model on raised useful answers from 7% to 57% — and moved safety by zero.", {
    x: M, y: 4.15, w: W, h: 0.5, fontFace: B, fontSize: 18, color: INK, margin: 0,
  });
  s.addText("That is the whole argument: the model was never allowed near the decision.", {
    x: M, y: 4.68, w: W, h: 0.5, fontFace: B, fontSize: 16, color: TEAL, italic: true, margin: 0,
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 5.45, w: W, h: 1.0, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.12,
  });
  s.addText(
    [
      { text: "Also:  ", options: { color: MUT } },
      { text: "56 automated tests", options: { color: INK, bold: true } },
      { text: "   ·   ", options: { color: MUT } },
      { text: "works with no model reachable", options: { color: INK, bold: true } },
      { text: "   ·   ", options: { color: MUT } },
      { text: "full Arabic interface", options: { color: INK, bold: true } },
    ],
    { x: M + 0.45, y: 5.45, w: W - 0.9, h: 1.0, fontFace: B, fontSize: 15, valign: "middle", margin: 0 },
  );
  s.addNotes("Lead with the two 100% rows side by side. The 7% -> 57% line is the punchline.");
}

/* ───────────────────────── 9. close ───────────────────────── */
{
  const s = slide();
  s.addShape(pres.ShapeType.ellipse, {
    x: 8.9, y: 2.2, w: 7.0, h: 7.0, fill: { color: CARD }, line: { color: CARD },
  });

  kicker(s, "WHAT I TOOK AWAY");
  s.addText("The work isn't making the model smarter.", {
    x: M, y: 2.1, w: 8.9, h: 1.0, fontFace: H, fontSize: 33, bold: true, color: INK, margin: 0,
  });
  s.addText("It's making sure it can't be wrong\nin a way that matters.", {
    x: M, y: 3.15, w: 8.9, h: 1.3, fontFace: H, fontSize: 33, bold: true, color: TEAL, margin: 0,
  });

  s.addText("Next: public deployment, a larger medicine registry, and a pharmacist trial.", {
    x: M, y: 5.0, w: 8.9, h: 0.5, fontFace: B, fontSize: 15, color: MUT, margin: 0,
  });
  s.addText("Thank you — questions welcome.", {
    x: M, y: 6.2, w: 8.9, h: 0.5, fontFace: B, fontSize: 17, color: INK, bold: true, margin: 0,
  });
  s.addNotes("Say the two lines slowly. Then stop talking and take questions.");
}

pres.writeFile({ fileName: process.argv[2] || "Badeel.pptx" }).then((f) => console.log("wrote", f));
