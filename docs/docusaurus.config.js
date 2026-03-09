const config = {
  title: "codeDown",
  tagline: "Markdown to themed PDF",
  url: "https://bouajilaprog.github.io",
  baseUrl: "/CodeDown/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  organizationName: "bouajilaProg",
  projectName: "CodeDown",

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          routeBasePath: "/",
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: "codeDown",
      items: [
        {
          href: "https://github.com/bouajilaProg/CodeDown",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      copyright: `Copyright © ${new Date().getFullYear()} bouajilaProg`,
    },
  },
};

module.exports = config;
