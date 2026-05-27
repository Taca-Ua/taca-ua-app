export const normalizeText = (text: string) => {
  return text
    .normalize("NFD") // separates accents from letters
    .replace(/[\u0300-\u036f]/g, "") // removes accents
    .replace(/[^\w\s]/g, "") // removes punctuation
    .toLowerCase()
    .trim();
};
