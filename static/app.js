/**
 * Multi-Prime RSA Analyzer - Frontend Logic
 * Menangani generate key, enkripsi, dan dekripsi.
 * Bebas dependensi eksternal, rapi, aman dari XSS.
 */

document.addEventListener("DOMContentLoaded", () => {
  const state = {
    currentKey: null,
    lastCiphertext: null
  };

  // Helper untuk mengubah angka integer ke subscript unicode (misal: 1 -> ₁, 2 -> ₂)
  function toSubscript(num) {
    const subMap = {
      '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
      '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    };
    return String(num).split('').map(ch => subMap[ch] || ch).join('');
  }

  // ---------------- Navigasi Tab ----------------
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });

  // ---------------- Tombol Salin ----------------
  document.addEventListener("click", (e) => {
    if (e.target && e.target.classList.contains("copy-btn")) {
      const targetId = e.target.getAttribute("data-target");
      let textToCopy = "";
      if (targetId === "pub-data" && state.currentKey) {
        textToCopy = JSON.stringify(state.currentKey.public_key, null, 2);
      } else if (targetId === "priv-data" && state.currentKey) {
        textToCopy = JSON.stringify(state.currentKey.private_key, null, 2);
      } else {
        const el = document.getElementById(targetId);
        if (el) textToCopy = el.textContent;
      }
      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
          const originalText = e.target.textContent;
          e.target.textContent = "Disalin!";
          setTimeout(() => { e.target.textContent = originalText; }, 1500);
        });
      }
    }
  });

  // ---------------- Helper Text ----------------
  function setSafeText(elementId, text) {
    const el = document.getElementById(elementId);
    if (el) {
      el.textContent = text !== undefined && text !== null ? String(text) : "-";
    }
  }

  // ---------------- 1. Generate Key ----------------
  const formKeygen = document.getElementById("form-keygen");
  const keygenStatus = document.getElementById("keygen-status");
  const keygenResults = document.getElementById("keygen-results");
  const btnGenKeys = document.getElementById("btn-generate-keys");

  formKeygen.addEventListener("submit", async (e) => {
    e.preventDefault();
    const bits = parseInt(document.getElementById("keygen-bits").value, 10);
    const k = parseInt(document.getElementById("keygen-k").value, 10);

    btnGenKeys.disabled = true;
    keygenStatus.className = "status-msg";
    keygenStatus.textContent = "Sedang membuat bilangan prima dan pasangan kunci...";
    keygenStatus.classList.remove("hidden");
    keygenResults.classList.add("hidden");

    try {
      const resp = await fetch("/keygen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bits, k })
      });
      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.error || "Generate key gagal.");
      }

      state.currentKey = data;
      renderKeygenResults(data);
      keygenStatus.className = "status-msg success";
      keygenStatus.textContent = `Pasangan kunci berhasil dibuat: modulus ${data.public_key.bits} bit dengan ${k} faktor prima.`;
      keygenResults.classList.remove("hidden");
    } catch (err) {
      keygenStatus.className = "status-msg error";
      keygenStatus.textContent = "Terjadi kesalahan: " + err.message;
    } finally {
      btnGenKeys.disabled = false;
    }
  });

  function renderKeygenResults(data) {
    const pub = data.public_key;
    const priv = data.private_key;

    // Kunci Publik
    setSafeText("pub-n", pub.n);
    setSafeText("pub-e", pub.e);
    setSafeText("pub-bits", `${pub.bits} bit`);
    setSafeText("pub-k", `${pub.k} prima`);

    // Kunci Privat
    setSafeText("priv-d", priv.d);

    // Daftar Prima
    const primesContainer = document.getElementById("priv-primes");
    primesContainer.innerHTML = "";
    priv.primes.forEach((p, idx) => {
      const chip = document.createElement("div");
      chip.className = "prime-chip";
      chip.textContent = `p${toSubscript(idx + 1)}: ${p}`;
      primesContainer.appendChild(chip);
    });

    // Eksponen privat per prima
    const dPrimesContainer = document.getElementById("priv-d-primes");
    dPrimesContainer.innerHTML = "";
    priv.d_primes.forEach((dp, idx) => {
      const chip = document.createElement("div");
      chip.className = "prime-chip";
      chip.textContent = `d${toSubscript(idx + 1)}: ${dp}`;
      dPrimesContainer.appendChild(chip);
    });

    // Koefisien Garner
    const tCoeffsContainer = document.getElementById("priv-t-coeffs");
    tCoeffsContainer.innerHTML = "";
    priv.t_coeffs.forEach((t, idx) => {
      const chip = document.createElement("div");
      chip.className = "prime-chip";
      chip.textContent = `t${toSubscript(idx + 2)}: ${t}`;
      tCoeffsContainer.appendChild(chip);
    });
  }

  // Gunakan kunci pada tab enkripsi
  document.getElementById("btn-use-keys").addEventListener("click", () => {
    if (!state.currentKey) return;
    document.getElementById("enc-n").value = state.currentKey.public_key.n;
    document.getElementById("enc-e").value = state.currentKey.public_key.e;

    // Berpindah ke tab Enkripsi & Dekripsi
    document.querySelector('[data-tab="tab-crypto"]').click();
  });

  // ---------------- 2. Enkripsi ----------------
  const formEncrypt = document.getElementById("form-encrypt");
  const encResult = document.getElementById("enc-result");
  const encOutput = document.getElementById("enc-output");

  formEncrypt.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mode = document.querySelector('input[name="enc-mode"]:checked').value;
    const isText = mode === "text";
    const message = document.getElementById("enc-input").value;
    const n = document.getElementById("enc-n").value.trim();
    const eVal = document.getElementById("enc-e").value.trim();

    if (!n || !eVal) {
      alert("Isi modulus (n) dan eksponen publik (e). Gunakan tombol Generate Key untuk mengisi otomatis.");
      return;
    }

    try {
      const resp = await fetch("/encrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, is_text: isText, n, e: eVal })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Enkripsi pesan gagal.");

      if (isText) {
        state.lastCiphertext = data.ciphertext_blocks;
        encOutput.textContent = JSON.stringify(data.ciphertext_blocks);
      } else {
        state.lastCiphertext = data.ciphertext;
        encOutput.textContent = data.ciphertext;
      }
      encResult.classList.remove("hidden");
    } catch (err) {
      alert("Enkripsi gagal: " + err.message);
    }
  });

  document.getElementById("btn-forward-cipher").addEventListener("click", () => {
    if (!state.lastCiphertext) return;
    const decInput = document.getElementById("dec-cipher");
    if (Array.isArray(state.lastCiphertext)) {
      decInput.value = JSON.stringify(state.lastCiphertext);
    } else {
      decInput.value = state.lastCiphertext;
    }
  });

  // ---------------- 3. Dekripsi ----------------
  const formDecrypt = document.getElementById("form-decrypt");
  const decResult = document.getElementById("dec-result");
  const decOutputText = document.getElementById("dec-output-text");
  const decMetrics = document.getElementById("dec-metrics");
  const decStepsContent = document.getElementById("dec-steps-content");
  const decMethodBadge = document.getElementById("dec-method-badge");

  formDecrypt.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.currentKey) {
      alert("Buat pasangan kunci terlebih dahulu melalui tab Generate Key.");
      return;
    }

    const rawCipher = document.getElementById("dec-cipher").value.trim();
    if (!rawCipher) {
      alert("Masukkan ciphertext (hasil enkripsi) terlebih dahulu.");
      return;
    }

    const method = document.getElementById("dec-method").value;
    const isTextMode = document.querySelector('input[name="enc-mode"]:checked').value === "text";

    let cipherPayload;
    if (isTextMode) {
      try {
        cipherPayload = JSON.parse(rawCipher);
      } catch {
        cipherPayload = rawCipher.replace(/[\[\],]/g, " ").split(/\s+/).filter(Boolean);
      }
    } else {
      cipherPayload = rawCipher;
    }

    try {
      const resp = await fetch("/decrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ciphertext: cipherPayload,
          is_text: isTextMode,
          method: method,
          key_data: state.currentKey.private_key
        })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Dekripsi pesan gagal.");

      renderDecryptionResult(data, method, isTextMode);
      decResult.classList.remove("hidden");
    } catch (err) {
      alert("Dekripsi gagal: " + err.message);
    }
  });

  function renderDecryptionResult(data, method, isText) {
    if (isText) {
      decOutputText.textContent = data.recovered_text;
    } else {
      decOutputText.textContent = data.plaintext;
    }

    decMetrics.innerHTML = "";
    const timeMs = (isText ? data.total_execution_time_s : data.execution_time_s) * 1000.0;

    const bTime = document.createElement("div");
    bTime.className = "metric-badge";
    bTime.innerHTML = `Waktu dekripsi: <strong>${timeMs.toFixed(3)} ms</strong>`;
    decMetrics.appendChild(bTime);

    const ops = isText && data.sample_block_intermediate_steps
      ? data.sample_block_intermediate_steps.operation_counts
      : data.operation_counts;

    if (ops) {
      const bOps = document.createElement("div");
      bOps.className = "metric-badge";
      bOps.innerHTML = `Operasi: <strong>${ops.multiplications} perkalian</strong> | <strong>${ops.modulo_ops} modulo</strong>`;
      decMetrics.appendChild(bOps);
    }

    decMethodBadge.textContent = method.toUpperCase();

    // Langkah antara
    const steps = isText ? data.sample_block_intermediate_steps : data.intermediate_steps;
    decStepsContent.innerHTML = "";

    if (!steps) return;

    if (method === "standard") {
      const div = document.createElement("div");
      div.className = "calc-explanation";
      div.innerHTML = `
        <strong>RSA Standar:</strong><br>
        m = cᵈ mod n<br>
        Pesan hasil dekripsi: <code>${steps.m}</code>
      `;
      decStepsContent.appendChild(div);
    } else if (method === "crt_garner") {
      const h5Primes = document.createElement("h5");
      h5Primes.textContent = "Tahap 1: Hitung hasil dekripsi pada tiap prima (cᵢ = c mod pᵢ, mᵢ = cᵢ^(dᵢ) mod pᵢ)";
      h5Primes.style.marginBottom = "8px";
      decStepsContent.appendChild(h5Primes);

      const table = document.createElement("table");
      table.className = "steps-table";
      table.innerHTML = `
        <thead>
          <tr>
            <th>Prima (pᵢ)</th>
            <th>Eksponen privat per prima (dᵢ)</th>
            <th>Sisa ciphertext (cᵢ)</th>
            <th>Hasil dekripsi per prima (mᵢ)</th>
          </tr>
        </thead>
        <tbody></tbody>
      `;
      const tbody = table.querySelector("tbody");
      steps.per_prime.forEach((item, idx) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>p${toSubscript(idx + 1)} = ${item.p_i}</td>
          <td>d${toSubscript(idx + 1)} = ${item.d_i}</td>
          <td>c${toSubscript(idx + 1)} = ${item.c_i}</td>
          <td><strong>m${toSubscript(idx + 1)} = ${item.m_i}</strong></td>
        `;
        tbody.appendChild(row);
      });
      decStepsContent.appendChild(table);

      const h5Garner = document.createElement("h5");
      h5Garner.textContent = "Tahap 2: Gabungkan hasil dengan metode Garner";
      h5Garner.style.marginTop = "14px";
      h5Garner.style.marginBottom = "8px";
      decStepsContent.appendChild(h5Garner);

      const initP = document.createElement("p");
      initP.style.fontSize = "0.85rem";
      initP.textContent = `Nilai awal: x = m₁ = ${steps.per_prime[0].m_i}`;
      decStepsContent.appendChild(initP);

      steps.garner_steps.forEach(st => {
        const subI = toSubscript(st.step);
        const stepDiv = document.createElement("div");
        stepDiv.className = "garner-walkthrough-step";
        stepDiv.innerHTML = `
          <strong>Langkah ke-${st.step} (untuk p${subI}):</strong><br>
          &bull; diff = (${st.m_i} - ${st.x_prev}) mod ${st.p_i} = <code>${st.diff}</code><br>
          &bull; u${subI} = (${st.diff} × ${st.t_i}) mod ${st.p_i} = <code>${st.u}</code><br>
          &bull; Nilai Baru x = <strong>${st.x_new}</strong>
        `;
        decStepsContent.appendChild(stepDiv);
      });
    } else if (method === "crt_gauss" || method === "crt_gauss_legacy") {
      const h5Gauss = document.createElement("h5");
      h5Gauss.textContent = "Gabungkan hasil dengan metode CRT-Gauss:";
      decStepsContent.appendChild(h5Gauss);

      const tableG = document.createElement("table");
      tableG.className = "steps-table";
      tableG.innerHTML = `
        <thead>
          <tr>
            <th>Prima (pᵢ)</th>
            <th>mᵢ</th>
            ${steps.precomputed
              ? "<th>Cᵢ = Nᵢ·Mᵢ mod n (prekomputasi saat pembangkitan kunci)</th>"
              : "<th>Nᵢ = n / pᵢ</th><th>Mᵢ = Nᵢ⁻¹ mod pᵢ</th>"}
          </tr>
        </thead>
        <tbody></tbody>
      `;
      const tbodyG = tableG.querySelector("tbody");
      steps.gauss_steps.forEach((st, idx) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>p${toSubscript(idx + 1)} = ${st.p_i}</td>
          <td>${st.m_i}</td>
          ${steps.precomputed
            ? `<td><code>${st.C_i}</code></td>`
            : `<td><code>${st.N_i}</code></td><td>${st.M_i}</td>`}
        `;
        tbodyG.appendChild(row);
      });
      decStepsContent.appendChild(tableG);
    }
  }
});
