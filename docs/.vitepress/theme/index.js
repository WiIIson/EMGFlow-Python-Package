import DefaultTheme from 'vitepress/theme';
import './custom.css';

export default {
  ...DefaultTheme,
  enhanceApp({ app }) {
    app.mount(() => {
      document.addEventListener("DOMContentLoaded", function () {
        setTimeout(() => {
          document.querySelectorAll("svg .mindmap-node").forEach((node) => {
            // Collect all text within tspans
            const tspans = node.querySelectorAll("tspan");
            let nodeName = Array.from(tspans).map(tspan => tspan.textContent.trim()).join(" ");

            // Define mapping of nodes to links
            const links = {
                "Extract Features": "https://wiiison.github.io/EMGFlow-Python-Package/reference/feature-extraction.html",
                "File Access": "https://wiiison.github.io/EMGFlow-Python-Package/reference/file-access.html",
                "Detect Outliers": "https://wiiison.github.io/EMGFlow-Python-Package/reference/outlier-detection.html",
                "Plot Signals": "https://wiiison.github.io/EMGFlow-Python-Package/reference/plot-signals.html",
                "Preprocess Signals": "https://wiiison.github.io/EMGFlow-Python-Package/reference/preprocess-signals.html",
            };

            if (links[nodeName]) {
                node.style.cursor = "pointer"; // Indicate clickability
                node.addEventListener("click", () => {
                    window.location.href = links[nodeName]; // Redirect to the corresponding page
                });
            }
          });
        }, 500); // Allow time for Mermaid rendering
      });
    });
  }
}