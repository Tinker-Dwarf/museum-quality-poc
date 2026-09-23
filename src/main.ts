import "./style.css";
import { createStudio } from "./studio/createStudio";
import { renderShell, wireChrome } from "./ui/chrome";

const app = document.querySelector<HTMLDivElement>("#app")!;
const viewport = renderShell(app);

const studio = createStudio({
  mount: viewport,
});

wireChrome(app, studio);

requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
