const frenchStopwords: Set<string> = new Set([
  'a',
  'à',
  'de',
  'des',
  'la',
  'le',
  'les',
  'et',
  'en',
  'chez',
  'par',
  'dans',
  'exploitation',
  'pour',
  'cadre',
])

export const slugify = (text: string): string => {
  // Remove stopwords and letters with apostrophes from text
  const textWithoutStopwords = text
    .split(' ')
    .map((word) => word.toLowerCase())
    .filter((word) => !frenchStopwords.has(word) && !/\b[dl](’|')\b/.test(word))
    .slice(0, 3)
    .join(' ')

  // Remove non-word characters and replace spaces with hyphens
  let slug = textWithoutStopwords
    .replace(/[^\w\s-]/g, '')
    .trim()
    .toLowerCase()

  // Normalize the slug to remove diacritics and accents
  slug = slug.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')

  return slug
}
