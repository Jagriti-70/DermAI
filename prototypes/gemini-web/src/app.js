// ── DermAI — Skin Disease Early Detection ───────────────────────

(function () {
  "use strict";

  // ── State ──────────────────────────────────────────────────────
  let apiKey = sessionStorage.getItem("dermai_key") || "";
  let currentBase64 = null;
  let currentMime = "image/jpeg";

  // ── Elements ───────────────────────────────────────────────────
  const dropZone       = document.getElementById("dropZone");
  const fileInput      = document.getElementById("fileInput");
  const dropContent    = document.getElementById("dropContent");
  const previewContent = document.getElementById("previewContent");
  const previewImg     = document.getElementById("previewImg");
  const scanImg        = document.getElementById("scanImg");
  const analyzeBtn     = document.getElementById("analyzeBtn");
  const resetBtn       = document.getElementById("resetBtn");
  const retryBtn       = document.getElementById("retryBtn");
  const apiKeyInput    = document.getElementById("apiKeyInput");
  const saveKeyBtn     = document.getElementById("saveKeyBtn");

  // Results
  const resultsIdle    = document.getElementById("resultsIdle");
  const resultsLoading = document.getElementById("resultsLoading");
  const resultsOutput  = document.getElementById("resultsOutput");
  const resultsError   = document.getElementById("resultsError");
  const errorMsg       = document.getElementById("errorMsg");

  const primaryDiagnosis  = document.getElementById("primaryDiagnosis");
  const riskValue         = document.getElementById("riskValue");
  const confPct           = document.getElementById("confPct");
  const confFill          = document.getElementById("confFill");
  const differentialsList = document.getElementById("differentialsList");
  const findingsText      = document.getElementById("findingsText");
  const recText           = document.getElementById("recText");

  // Loading steps
  const steps = [
    document.getElementById("step1"),
    document.getElementById("step2"),
    document.getElementById("step3"),
    document.getElementById("step4"),
  ];

  // ── Init ───────────────────────────────────────────────────────
  if (apiKey) apiKeyInput.value = apiKey;

  // ── API Key ────────────────────────────────────────────────────
  saveKeyBtn.addEventListener("click", () => {
    const val = apiKeyInput.value.trim();
    if (!val) { alert("Please enter your Gemini API key."); return; }
    apiKey = val;
    sessionStorage.setItem("dermai_key", apiKey);
    saveKeyBtn.textContent = "✓ Saved";
    setTimeout(() => { saveKeyBtn.textContent = "Save"; }, 1800);
  });

  // ── Drag & Drop ────────────────────────────────────────────────
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) loadImage(file);
  });
  dropZone.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-change") || e.target.tagName === "LABEL") return;
    if (!currentBase64) fileInput.click();
  });
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) loadImage(fileInput.files[0]);
  });

  // ── Load Image ─────────────────────────────────────────────────
  function loadImage(file) {
    currentMime = file.type || "image/jpeg";
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      currentBase64 = dataUrl.split(",")[1];
      previewImg.src = dataUrl;
      scanImg.src = dataUrl;
      dropContent.style.display = "none";
      previewContent.style.display = "block";
      analyzeBtn.disabled = false;
      showState("idle");
    };
    reader.readAsDataURL(file);
  }

  // ── Show State ─────────────────────────────────────────────────
  function showState(state) {
    resultsIdle.style.display    = state === "idle"    ? "flex" : "none";
    resultsLoading.style.display = state === "loading" ? "flex" : "none";
    resultsOutput.style.display  = state === "output"  ? "flex" : "none";
    resultsError.style.display   = state === "error"   ? "flex" : "none";
  }

  // ── Reset ──────────────────────────────────────────────────────
  function resetAll() {
    currentBase64 = null;
    fileInput.value = "";
    dropContent.style.display = "flex";
    previewContent.style.display = "none";
    analyzeBtn.disabled = true;
    showState("idle");
  }

  if (resetBtn) resetBtn.addEventListener("click", resetAll);
  if (retryBtn) retryBtn.addEventListener("click", resetAll);

  // ── Loading Step Animator ──────────────────────────────────────
  let stepTimer = null;
  function animateSteps() {
    steps.forEach(s => { s.classList.remove("active", "done"); });
    steps[0].classList.add("active");
    let i = 0;
    stepTimer = setInterval(() => {
      if (i < steps.length - 1) {
        steps[i].classList.remove("active");
        steps[i].classList.add("done");
        i++;
        steps[i].classList.add("active");
      }
    }, 1200);
  }
  function stopSteps() {
    clearInterval(stepTimer);
    steps.forEach(s => { s.classList.remove("active", "done"); });
  }

  // ── Analyze ────────────────────────────────────────────────────
  analyzeBtn.addEventListener("click", async () => {
    if (!apiKey) {
      alert("Please enter and save your Gemini API key first.");
      apiKeyInput.focus();
      return;
    }
    if (!currentBase64) return;

    showState("loading");
    analyzeBtn.disabled = true;
    animateSteps();

    const prompt = `You are a dermatology AI assistant trained on the HAM10000 and ISIC datasets, specializing in skin disease classification using CNN-based deep learning (EfficientNet/ResNet architecture).

Analyze this skin image and respond ONLY with a valid JSON object — no markdown, no backticks, no text outside the JSON.

{
  "primary_diagnosis": "Most likely skin condition name (e.g. Melanocytic Nevus, Melanoma, Basal Cell Carcinoma, Actinic Keratosis, Benign Keratosis, Dermatofibroma, Vascular Lesion, Psoriasis, Eczema, Fungal Infection, or other dermatological condition)",
  "confidence": 85,
  "risk_level": "low" | "medium" | "high",
  "differentials": [
    { "name": "Condition 1", "probability": 85 },
    { "name": "Condition 2", "probability": 10 },
    { "name": "Condition 3", "probability": 5 }
  ],
  "clinical_findings": "2-3 sentences describing the visual features observed: lesion morphology, color, border characteristics, texture, size estimation, and any ABCDE criteria relevant to the finding.",
  "recommendation": "Clinical recommendation for follow-up action based on risk level (e.g. routine monitoring, dermatologist consultation within X weeks, urgent referral)."
}

Rules:
- confidence is integer 0–100
- risk_level is exactly one of: low, medium, high
- differentials has 2–4 items, probabilities sum to ~100
- If the image is NOT a skin image at all, set primary_diagnosis to "Non-dermatological image" with low confidence
- Be clinically precise and use proper dermatological terminology`;

    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{
            parts: [
              { inline_data: { mime_type: currentMime, data: currentBase64 } },
              { text: prompt }
            ]
          }],
          generationConfig: { temperature: 0.1, maxOutputTokens: 1024 }
        })
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        if (response.status === 403 || response.status === 400)
          throw new Error("Invalid API key. Please check your Gemini API key and try again.");
        throw new Error(err?.error?.message || `API error ${response.status}`);
      }

      const data = await response.json();
      const rawText = data?.candidates?.[0]?.content?.parts
        ?.filter(p => p.text)?.map(p => p.text)?.join("") || "";

      if (!rawText) throw new Error("Empty response from Gemini. Please try again.");

      const clean = rawText.replace(/```json|```/g, "").trim();
      let parsed;
      try {
        parsed = JSON.parse(clean);
      } catch {
        const match = clean.match(/\{[\s\S]*\}/);
        if (match) parsed = JSON.parse(match[0]);
        else throw new Error("Could not parse AI response. Please try again.");
      }

      stopSteps();
      renderResults(parsed);

    } catch (err) {
      stopSteps();
      errorMsg.textContent = err.message;
      showState("error");
      analyzeBtn.disabled = false;
    }
  });

  // ── Render Results ─────────────────────────────────────────────
  function renderResults(data) {
    // Primary diagnosis
    primaryDiagnosis.textContent = data.primary_diagnosis || "Unknown";

    // Risk
    const risk = (data.risk_level || "low").toLowerCase();
    riskValue.textContent = risk.charAt(0).toUpperCase() + risk.slice(1);
    riskValue.className = "risk-value " + risk;

    // Confidence
    const conf = Math.max(0, Math.min(100, parseInt(data.confidence) || 0));
    confPct.textContent = `${conf}%`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => { confFill.style.width = `${conf}%`; });
    });

    // Differentials
    differentialsList.innerHTML = "";
    const diffs = Array.isArray(data.differentials) ? data.differentials.slice(0, 4) : [];
    diffs.forEach(d => {
      const prob = Math.max(0, Math.min(100, parseInt(d.probability) || 0));
      const item = document.createElement("div");
      item.className = "diff-item";
      item.innerHTML = `
        <span class="diff-name">${d.name || "Unknown"}</span>
        <div class="diff-bar-wrap"><div class="diff-bar" style="width:0%" data-w="${prob}%"></div></div>
        <span class="diff-pct">${prob}%</span>
      `;
      differentialsList.appendChild(item);
    });

    // Animate differential bars
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        differentialsList.querySelectorAll(".diff-bar").forEach(bar => {
          bar.style.width = bar.dataset.w;
        });
      });
    });

    // Findings
    findingsText.textContent = data.clinical_findings || "No findings available.";

    // Recommendation
    recText.textContent = data.recommendation || "Consult a dermatologist for further evaluation.";

    showState("output");
    analyzeBtn.disabled = false;
  }

})();
