import DefaultTheme from 'vitepress/theme';
import './custom.css';

export default {
  ...DefaultTheme,
  enhanceApp({ app }) {
    app.mount(() => {
      document.addEventListener("DOMContentLoaded", function () {
        setTimeout(() => {
          document.querySelectorAll("svg g.node").forEach((node) => {
            const textElement = node.querySelector("text");
            if (textElement) {
              const nodeName = textElement.textContent.trim();
              const links = {
                "EF": "https://wiiison.github.io/EMGFlow-Python-Package/reference/feature-extraction.html",
                "FA": "https://wiiison.github.io/EMGFlow-Python-Package/reference/file-access.html",
                "DO": "https://wiiison.github.io/EMGFlow-Python-Package/reference/outlier-detection.html",
                "PlS": "https://wiiison.github.io/EMGFlow-Python-Package/reference/plot-signals.html",
                "PrS": "https://wiiison.github.io/EMGFlow-Python-Package/reference/preprocess-signals.html",
              };
              if (links[nodeName]) {
                node.style.cursor = "pointer";
                node.addEventListener("click", () => {
                  window.location.href = links[nodeName];
                });
              }
            }
          });
        }, 500);
      });
    });
  }
}