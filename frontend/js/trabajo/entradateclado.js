// ¿El programa lee del teclado? (Scanner, cin, scanf, input…) → la terminal pide los datos antes de enviarlo.
export const LEE_ENTRADA = {
  java: /\bScanner\b|System\.in\b|BufferedReader|System\.console\s*\(/,
  c: /\bscanf\s*\(|\bfgets\s*\(|\bgetchar\s*\(|\bgets\s*\(|\bgetline\s*\(/,
  cpp: /\bcin\b|\bgetline\s*\(|\bscanf\s*\(|\bgetchar\s*\(/,
  csharp: /Console\.Read(?:Line|Key)?\s*\(/,
  php: /STDIN|php:\/\/stdin|\breadline\s*\(/,
  go: /fmt\.(?:Scan|Fscan|Sscan)|os\.Stdin/,
  rust: /\bstdin\s*\(/,
  swift: /\breadLine\s*\(/,
  kotlin: /\breadLine\s*\(|\breadln\s*\(|\bScanner\s*\(/,
  ruby: /\bgets\b|STDIN|\$stdin|ARGF/,
  docker: /./,
  python: /\binput\s*\(|sys\.stdin|\bfileinput\b/,
};
