export async function openPhoto(src) {
  const { Fancybox } = await import("@fancyapps/ui/dist/fancybox/index.js");
  await import("@fancyapps/ui/dist/fancybox/fancybox.css");
  Fancybox.show([{ src, type: "image" }]);
}
