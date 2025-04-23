import DefaultTheme from 'vitepress/theme';
import './custom.css';

export default {
  ...DefaultTheme,
  enhanceApp({ app }) {                         // Workaround for mindmap links
    window.addEventListener('load', () => {
      document.querySelectorAll('*[class*="link:"]').forEach(node => {
        node.classList.forEach(className => {
          if (className.startsWith('link:')) {
            const url = className.split(':')[1];
            node.addEventListener('click', () => {
              window.open(`https://${url}`, '_blank');
            });
          }
        });
      });
    });
  },
};