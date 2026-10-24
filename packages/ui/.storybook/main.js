/** @type { import('storybook/internal/types').StorybookConfig } */
const config = {
  stories: ["../src/**/*.stories.@(js|jsx)"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  addons: ["@storybook/addon-docs"],
};

export default config;
