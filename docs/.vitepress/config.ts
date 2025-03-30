import { defineConfig } from 'vitepress';

// refer https://vitepress.dev/reference/site-config for details
export default defineConfig({
  lang: 'en-US',
  title: 'EMGFlow',
  description: 'EMG Workflow package.',
  base: '/EMGFlow-Python-Package/',

  themeConfig: {
    //nav: [
    //  { text: 'Example', link: '/example' },

      // {
      //   text: 'Dropdown Menu',
      //   items: [
      //     { text: 'Item A', link: '/item-1' },
      //     { text: 'Item B', link: '/item-2' },
      //     { text: 'Item C', link: '/item-3' },
      //   ],
      // },

      // ...
    //],

    sidebar: [
      {
        // text: 'Guide',
        items: [
          { text: 'Examples', link: '/01 Examples' },
          { text: 'Background', link: '/02 Background' },
          { text: 'Processing Pipeline', link: '/03 Processing Pipeline' },
          { text: 'FileAccess API', link: '/04 FileAccess API' },
          { text: 'PreprocessSignals API', link: '/05 PreprocessSignals API' },
          { text: 'ExtractFeatures API', link: '/06 ExtractFeatures API' },
          { text: 'OutlierFinder API', link: '/07 OutlierFinder API' },
          { text: 'PlotSignals API', link: '/08 PlotSignals API' },
          // ...
        ],
      },
    ],
  },
});
