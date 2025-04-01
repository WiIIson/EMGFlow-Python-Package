import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "EMGFlow",
  titleTemplate: 'EMG Workflow',
  description: "The open workflow for EMG signal processing and feature extraction",
  base: '/EMGFlow-Python-Package/',

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
          { text: 'Getting started', link: '/guide/getting-started' },
          { text: 'Examples', link: '/guide/examples' },
          { text: 'About electromyography', link: '/guide/about-emg' },
        ]
      },

      {
        text: 'Reference',
        items: [
          { text: 'Overview', link: '/reference/api-overview' },
          { text: 'Pre-processing', link: '/reference/preprocess-signals' },
          { text: 'Feature extraction', link: '/reference/feature-extraction' },
          { text: 'Plotting signals', link: '/reference/plot-signals' },
          { text: 'Outlier detection', link: '/reference/outlier-detection' },
          { text: 'File access', link: '/reference/file-access' },
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
})
