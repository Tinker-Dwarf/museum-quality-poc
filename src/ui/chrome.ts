import type { StudioApi } from "../studio/createStudio";
import { explodeArrows, eye, steamWaves, undo } from "./icons";

/** Minimal museum shell. Returns #viewport for WebGL. */
export function renderShell(root: HTMLElement): HTMLElement {
  root.innerHTML = `
    <div class="museum">
      <div id="viewport" class="viewport" aria-label="Museum locomotive study"></div>
      <div class="overlay" aria-hidden="false">
        <div class="scene-chips" aria-label="Study actions">
          <button type="button" id="explode-btn" class="explode-pill" aria-pressed="false">
            <span class="chip-ico">${explodeArrows}</span>
            <span id="explode-label">Explode</span>
          </button>
          <button type="button" id="steam-btn" class="chip-btn" aria-pressed="false" title="Steam">
            <span class="chip-ico">${steamWaves}</span>
            <span>Steam</span>
          </button>
          <button type="button" id="labels-btn" class="icon-btn round" aria-pressed="true" title="Labels" aria-label="Toggle labels">
            ${eye}
          </button>
          <button type="button" id="reset-btn" class="icon-btn round" title="Reset" aria-label="Reset">
            ${undo}
          </button>
        </div>
      </div>
    </div>
  `;
  return root.querySelector("#viewport")!;
}

export function wireChrome(root: HTMLElement, studio: StudioApi): void {
  let explodeOn = false;
  let steamOn = false;
  let labelsOn = true;

  const explodeBtn = root.querySelector<HTMLButtonElement>("#explode-btn")!;
  const steamBtn = root.querySelector<HTMLButtonElement>("#steam-btn")!;
  const labelsBtn = root.querySelector<HTMLButtonElement>("#labels-btn")!;
  const resetBtn = root.querySelector<HTMLButtonElement>("#reset-btn")!;

  explodeBtn.addEventListener("click", () => {
    explodeOn = !explodeOn;
    explodeBtn.setAttribute("aria-pressed", String(explodeOn));
    studio.setExplode(explodeOn ? 1 : 0);
  });

  steamBtn.addEventListener("click", () => {
    steamOn = !steamOn;
    steamBtn.setAttribute("aria-pressed", String(steamOn));
    steamBtn.classList.toggle("active", steamOn);
    studio.setSteam(steamOn);
  });

  labelsBtn.addEventListener("click", () => {
    labelsOn = !labelsOn;
    labelsBtn.setAttribute("aria-pressed", String(labelsOn));
    labelsBtn.classList.toggle("active", labelsOn);
  });

  resetBtn.addEventListener("click", () => {
    explodeOn = false;
    explodeBtn.setAttribute("aria-pressed", "false");
    studio.setExplode(0);
    studio.setView("both");
  });

  studio.setSteam(false);
  steamBtn.classList.remove("active");
  labelsBtn.classList.add("active");
}
