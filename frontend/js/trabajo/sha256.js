// SHA-256 por partes, para archivos que no conviene cargar enteros en memoria (crypto.subtle solo acepta el archivo completo).
const K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
  0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
  0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
  0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

export class Sha256 {
  constructor() {
    this.h = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
    this.w = new Uint32Array(64);
    this.resto = new Uint8Array(64);
    this.nResto = 0;
    this.largo = 0;
  }

  #bloque(d, o) {
    const w = this.w;
    for (let i = 0; i < 16; i += 1) w[i] = (d[o + i * 4] << 24) | (d[o + i * 4 + 1] << 16) | (d[o + i * 4 + 2] << 8) | d[o + i * 4 + 3];
    for (let i = 16; i < 64; i += 1) {
      const a = w[i - 15]; const b = w[i - 2];
      const s0 = ((a >>> 7) | (a << 25)) ^ ((a >>> 18) | (a << 14)) ^ (a >>> 3);
      const s1 = ((b >>> 17) | (b << 15)) ^ ((b >>> 19) | (b << 13)) ^ (b >>> 10);
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) | 0;
    }
    let [a, b, c, e, f, g, h, k] = this.h;
    let dd;
    for (let i = 0; i < 64; i += 1) {
      const S1 = ((f >>> 6) | (f << 26)) ^ ((f >>> 11) | (f << 21)) ^ ((f >>> 25) | (f << 7));
      const t1 = (k + S1 + ((f & g) ^ (~f & h)) + K[i] + w[i]) | 0;
      const S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
      const t2 = (S0 + ((a & b) ^ (a & c) ^ (b & c))) | 0;
      dd = e;
      k = h; h = g; g = f; f = (dd + t1) | 0; e = c; c = b; b = a; a = (t1 + t2) | 0;
    }
    const H = this.h;
    H[0] += a; H[1] += b; H[2] += c; H[3] += e; H[4] += f; H[5] += g; H[6] += h; H[7] += k;
  }

  actualizar(datos) {
    let i = 0;
    this.largo += datos.length;
    if (this.nResto) {
      const n = Math.min(64 - this.nResto, datos.length);
      this.resto.set(datos.subarray(0, n), this.nResto);
      this.nResto += n;
      i = n;
      if (this.nResto < 64) return this;
      this.#bloque(this.resto, 0);
      this.nResto = 0;
    }
    for (; i + 64 <= datos.length; i += 64) this.#bloque(datos, i);
    if (i < datos.length) { this.resto.set(datos.subarray(i)); this.nResto = datos.length - i; }
    return this;
  }

  hex() {
    const bits = this.largo * 8;
    const relleno = new Uint8Array(((this.nResto < 56 ? 56 : 120) - this.nResto) + 8);
    relleno[0] = 0x80;
    const v = new DataView(relleno.buffer);
    v.setUint32(relleno.length - 8, Math.floor(bits / 2 ** 32));
    v.setUint32(relleno.length - 4, bits >>> 0);
    const largo = this.largo;
    this.actualizar(relleno);
    this.largo = largo;
    return [...this.h].map((x) => (x >>> 0).toString(16).padStart(8, "0")).join("");
  }
}

/** Huella de un Blob/File leyéndolo por partes. */
export async function sha256Blob(blob) {
  const s = new Sha256();
  const lector = blob.stream().getReader();
  for (;;) {
    const { done, value } = await lector.read();
    if (done) break;
    s.actualizar(value);
  }
  return s.hex();
}
