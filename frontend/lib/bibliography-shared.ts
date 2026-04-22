export function sourceSlug(fileName: string): string {
  return fileName
    .toLowerCase()
    .replace(/\.pdf$/i, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function sourceAnchorId(fileName: string): string {
  return `source-${sourceSlug(fileName)}`;
}
