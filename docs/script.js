const demoCases = [
  {
    id: "commuter",
    title: "Mid-market commuter",
    predicted: "$14,900",
    range: "$12,000 - $18,000",
    confidence: "moderate",
    note:
      "Typical gasoline sedan profile with balanced mileage and age. Falls in a segment where model error is usually moderate.",
    fields: [
      "year=2016",
      "odometer=88,000",
      "condition=good",
      "fuel=gas",
      "transmission=automatic",
    ],
  },
  {
    id: "pickup",
    title: "Diesel utility pickup",
    predicted: "$26,400",
    range: "$21,000 - $33,000",
    confidence: "wider uncertainty",
    note:
      "Diesel/utility segment has larger spread in observed prices. Point estimate is useful, but segment-level uncertainty should be shown.",
    fields: [
      "year=2018",
      "odometer=125,000",
      "condition=excellent",
      "fuel=diesel",
      "type=pickup",
    ],
  },
  {
    id: "older",
    title: "Older low-price listing",
    predicted: "$6,700",
    range: "$5,100 - $8,900",
    confidence: "higher relative error risk",
    note:
      "Lower-price and older-age listings can show higher relative error, even when absolute-dollar error is not extreme.",
    fields: [
      "year=2008",
      "odometer=171,000",
      "condition=fair",
      "fuel=gas",
      "title_status=clean",
    ],
  },
];

function setActiveButton(targetId) {
  const buttons = document.querySelectorAll("[data-case-btn]");
  buttons.forEach((btn) => {
    const isActive = btn.dataset.caseBtn === targetId;
    btn.classList.toggle("active", isActive);
  });
}

function renderCase(caseObj) {
  const status = document.getElementById("demo-status");
  const loader = document.getElementById("demo-loader");
  const result = document.getElementById("demo-result");
  const title = document.getElementById("demo-title");
  const price = document.getElementById("demo-price");
  const range = document.getElementById("demo-range");
  const conf = document.getElementById("demo-confidence");
  const note = document.getElementById("demo-note");
  const fields = document.getElementById("demo-fields");

  status.textContent = `Running precomputed scenario: ${caseObj.title} ...`;
  loader.classList.add("on");
  result.style.display = "none";

  setTimeout(() => {
    title.textContent = caseObj.title;
    price.textContent = caseObj.predicted;
    range.textContent = caseObj.range;
    conf.textContent = caseObj.confidence;
    note.textContent = caseObj.note;
    fields.innerHTML = "";
    caseObj.fields.forEach((f) => {
      const li = document.createElement("li");
      li.textContent = f;
      fields.appendChild(li);
    });
    loader.classList.remove("on");
    result.style.display = "block";
    status.textContent = "Static demo complete (precomputed output for GitHub Pages).";
  }, 1150);
}

function initDemo() {
  const buttons = document.querySelectorAll("[data-case-btn]");
  if (!buttons.length) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.caseBtn;
      const target = demoCases.find((c) => c.id === id);
      if (!target) return;
      setActiveButton(id);
      renderCase(target);
    });
  });

  setActiveButton(demoCases[0].id);
  renderCase(demoCases[0]);
}

window.addEventListener("DOMContentLoaded", initDemo);
