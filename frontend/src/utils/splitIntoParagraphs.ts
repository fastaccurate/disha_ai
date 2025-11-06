export const splitIntoParagraphs = (text: string): string[] => {
  if (typeof text !== "string") {
    console.error("Input is not a string");
    return [];
  }

  const paragraphs = text
    .split("\n")
    .filter((paragraph) => paragraph.trim() !== "");
  return paragraphs;
};
