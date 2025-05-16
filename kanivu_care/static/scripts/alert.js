export function showAlert(type, title, message, action = null) {
  const existing = document.getElementById("popupOverlay");
  if (existing) existing.remove();

  // Inject styles once
  if (!document.getElementById("popup-style")) {
    const style = document.createElement("style");
    style.id = "popup-style";
    style.textContent = `
      .popup-overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease-in-out;
      }
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      .popup-box {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 40px 35px;
        width: 380px;
        max-width: 90%;
        text-align: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        animation: dropIn 0.5s ease-out;
      }
      @keyframes dropIn {
        from { transform: translateY(-60px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
      .popup-icon {
        font-size: 60px;
        margin-bottom: 20px;
        animation: popIcon 0.4s ease;
        width: 120px;
        height: 120px;
        display: inline-block;
      }
      .popup-icon.success svg,
      .popup-icon.error svg {
        stroke-width: 2.5;
        width: 120px;
        height: 120px;
      }
      @keyframes popIcon {
        0% { transform: scale(0.7); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
      }
      .popup-icon.success svg { stroke: #6effc4; }
      .popup-icon.error svg { stroke: #ff6e6e; }
      .popup-title {
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 12px;
      }
      .popup-message {
        font-size: 16px;
        margin-bottom: 28px;
      }
      .popup-close-btn {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 30px;
        font-size: 16px;
        cursor: pointer;
        transition: transform 0.2s ease;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
      }
      .popup-close-btn:hover {
        transform: scale(1.06);
      }
    `;
    document.head.appendChild(style);
  }

  // Create popup
  const overlay = document.createElement("div");
  overlay.id = "popupOverlay";
  overlay.className = "popup-overlay";

  const iconName = type === "success" ? "check-circle" : "x-circle";

  overlay.innerHTML = `
    <div class="popup-box">
      <div class="popup-icon ${type}">
        <i data-feather="${iconName}"></i>
      </div>
      <div class="popup-title">${title}</div>
      <div class="popup-message">${message}</div>
      <button class="popup-close-btn" id="popupActionBtn">OK</button>
    </div>
  `;

  document.body.appendChild(overlay);

  // Feather icon render
  if (window.feather) {
    feather.replace();
  } else {
    console.warn("Feather Icons not loaded. Add <script src='https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js'></script> to your HTML.");
  }

  // Button behavior
  document.getElementById("popupActionBtn").onclick = () => {
    document.getElementById("popupOverlay").remove();
    if (action != "ok"){
        return window.location.href=action;
    }
  };
}
