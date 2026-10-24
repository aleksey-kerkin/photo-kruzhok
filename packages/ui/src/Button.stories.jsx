import { Button } from "./Button.jsx";

export default {
  title: "Button",
  component: Button,
};

export const Primary = {
  args: {
    variant: "primary",
    children: "Сохранить",
  },
  render: ({ children, ...args }) => <Button {...args}>{children}</Button>,
};
