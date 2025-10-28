import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid';

// https://vitepress.dev/reference/site-config
export default withMermaid({
  title: "EMGFlow",
  titleTemplate: 'EMG Workflow',
  description: "The open workflow for EMG signal processing and feature extraction",
  base: '/EMGFlow-Python-Package/',
  markdown: {
    math: true
  },

  // Update time of last content
  // https://vitepress.dev/reference/default-theme-last-updated
  lastUpdated: true,

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Guide', link: '/guide/what-is-emgflow' }, 
      { text: 'Reference', link: '/reference/api-overview' },
      { text: 'About Us', link: '/about/authors'}
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'What is EMGFlow?', link: '/guide/what-is-emgflow' },
          { text: 'Processing Steps', link: '/guide/processing-steps' },
          { text: 'Examples', link: '/guide/examples' },
          { text: 'About Electromyography', link: '/guide/about-emg' },
        ]
      },

      {
        text: 'Reference',
        items: [
          { text: 'Overview', link: '/reference/api-overview' },
          { text: 'File Format', link: '/reference/file-format' },
          { text: 'Access Files', link: '/reference/access-files' },
          { text: 'Preprocess Signals', link: '/reference/preprocess-signals' },
          { text: 'Plot Signals', link: '/reference/plot-signals' },
          { text: 'Extract Features', link: '/reference/extract-features' },
          { text: 'Testing', link: '/reference/testing', }
        ]
      },

      {
        text: 'About Us',
        items: [
          { text: 'Authors', link: '/about/authors' },
          { text: 'Citation', link: '/about/citation' },
          { text: 'Contact us', link: '/about/contact' },
        ]
      }, 
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/WiIIson/EMGFlow-Python-Package' }
    ],

    // Site footer
    footer: {
      message: 'Site built with <a href="https://vitepress.dev/">VitePress</a>',
      copyright: 'Created by <a href="https://wconley.ca/">William Conley</a> and <a href="https://affectivedatascience.com">Steven R. Livingstone</a>'
    }, 

    // Local search bar
    search: {
      provider: 'local'
    },

    // Add logo to navbar before site title (top left corner)
    logo: './EMGFlow.png',
  },
  mermaid:{},
});