import { test } from "node:test";
import assert from "node:assert/strict";
Object.defineProperty(globalThis, "navigator", { value: { languages: ["es-CO"], language: "es-CO", userAgent: "Android" }, configurable: true });
const { unirContactos, telInternacional, enlacesInvitacion } = await import("../js/contactos.js");

test("une contactos repetidos por número, correo o nombre", () => {
  const r = unirContactos([
    { nombre: "Ana Gómez", tel: ["300 123 4567"], email: [] },
    { nombre: "Ana Gómez", tel: ["+57 300-123-4567"], email: ["ana@x.com"] },
    { nombre: "ana gomez", tel: [], email: ["ANA@x.com"] },
    { nombre: "Luis", tel: ["3109998877"], email: [] },
    { nombre: "", tel: ["3109998877"], email: [] },
  ]);
  assert.equal(r.length, 2);
  const ana = r.find((c) => c.nombre === "Ana Gómez");
  assert.equal(ana.tel.length, 1);
  assert.deepEqual(ana.email, ["ana@x.com"]);
});

test("WhatsApp y SMS con número internacional", () => {
  assert.equal(telInternacional("300 123 4567", "57"), "573001234567");
  assert.equal(telInternacional("+1 (555) 010-2000", "57"), "15550102000");
  assert.equal(telInternacional("0057 3001234567", "57"), "573001234567");
  const e = enlacesInvitacion({ tel: ["3001234567"] }, "https://x/i");
  assert.match(e.whatsapp, /^https:\/\/wa\.me\/573001234567\?text=/);
  assert.match(e.sms, /^sms:\+573001234567\?body=/);
});
