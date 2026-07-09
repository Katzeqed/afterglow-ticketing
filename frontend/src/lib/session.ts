// Анонимный идентификатор клиента для холдов. Генерим один раз, храним локально.
// crypto.getRandomValues работает и по http (в отличие от crypto.randomUUID).

const KEY = "ag_session_token";

function randomHex(bytes: number): string {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  return Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join("");
}

export function getSessionToken(): string {
  let token = localStorage.getItem(KEY);
  if (!token) {
    token = `sess-${randomHex(16)}`;
    localStorage.setItem(KEY, token);
  }
  return token;
}

export function newIdempotencyKey(): string {
  return `idem-${randomHex(16)}`;
}
