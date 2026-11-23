// Módulos de Expo simulados para el celular de Aprende. Imitan la API real para que los ejemplos funcionen
// en el navegador; en un celular de verdad se usan los paquetes reales (npx expo install ...).
import React, { useState } from "react";
import { Image, Pressable, Text, View } from "react-native";

const h = React.createElement;
const espera = (v) => Promise.resolve(v);
const concedido = { status: "granted", granted: true, canAskAgain: true };

/* expo-status-bar */
export const StatusBar = () => null;

/* @react-native-async-storage/async-storage (se guarda en el navegador) */
const LS = (() => { try { localStorage.length; return localStorage; } catch { const m = new Map(); return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k), key: (i) => [...m.keys()][i] ?? null, get length() { return m.size; } }; } })();
const PRE = "rn:";
export const AsyncStorage = {
  getItem: async (k) => LS.getItem(PRE + k),
  setItem: async (k, v) => { if (typeof v !== "string") console.error("AsyncStorage solo guarda texto: usa JSON.stringify(objeto)"); LS.setItem(PRE + k, String(v)); },
  removeItem: async (k) => LS.removeItem(PRE + k),
  mergeItem: async (k, v) => LS.setItem(PRE + k, JSON.stringify({ ...JSON.parse(LS.getItem(PRE + k) || "{}"), ...JSON.parse(v) })),
  getAllKeys: async () => Array.from({ length: LS.length }, (_, i) => LS.key(i)).filter((k) => k?.startsWith(PRE)).map((k) => k.slice(PRE.length)),
  multiGet: async (ks) => ks.map((k) => [k, LS.getItem(PRE + k)]),
  multiSet: async (pares) => pares.forEach(([k, v]) => LS.setItem(PRE + k, v)),
  clear: async () => (await AsyncStorage.getAllKeys()).forEach((k) => LS.removeItem(PRE + k)),
};

/* expo-secure-store */
export const SecureStore = {
  setItemAsync: async (k, v) => LS.setItem("seguro:" + k, v),
  getItemAsync: async (k) => LS.getItem("seguro:" + k),
  deleteItemAsync: async (k) => LS.removeItem("seguro:" + k),
};

/* expo-haptics */
export const Haptics = {
  ImpactFeedbackStyle: { Light: "light", Medium: "medium", Heavy: "heavy", Soft: "soft", Rigid: "rigid" },
  NotificationFeedbackType: { Success: "success", Warning: "warning", Error: "error" },
  impactAsync: async (s = "medium") => { console.log("📳 Vibración " + s); try { navigator.vibrate?.(30); } catch {} },
  notificationAsync: async (t = "success") => { console.log("📳 Vibración " + t); try { navigator.vibrate?.([30, 40, 30]); } catch {} },
  selectionAsync: async () => { try { navigator.vibrate?.(10); } catch {} },
};

/* expo-location */
export const Location = {
  Accuracy: { Lowest: 1, Low: 2, Balanced: 3, High: 4, Highest: 5 },
  requestForegroundPermissionsAsync: async () => concedido,
  getForegroundPermissionsAsync: async () => concedido,
  getCurrentPositionAsync: () => new Promise((ok) => {
    const bogota = { coords: { latitude: 4.711, longitude: -74.0721, accuracy: 30, altitude: 2640 }, timestamp: Date.now() };
    try { navigator.geolocation.getCurrentPosition((p) => ok({ coords: p.coords, timestamp: p.timestamp }), () => ok(bogota), { timeout: 3000 }); } catch { ok(bogota); }
  }),
  reverseGeocodeAsync: async () => [{ city: "Bogotá", country: "Colombia", region: "Bogotá D.C." }],
};

/* expo-image-picker */
function elegirArchivo(accept) {
  return new Promise((ok) => {
    const i = document.createElement("input");
    i.type = "file"; i.accept = accept;
    i.onchange = () => { const f = i.files?.[0]; ok(f ? { canceled: false, assets: [{ uri: URL.createObjectURL(f), width: 0, height: 0, fileName: f.name, type: "image" }] } : { canceled: true, assets: null }); };
    i.oncancel = () => ok({ canceled: true, assets: null });
    i.click();
  });
}
export const ImagePicker = {
  MediaTypeOptions: { Images: "Images", Videos: "Videos", All: "All" },
  requestMediaLibraryPermissionsAsync: async () => concedido,
  requestCameraPermissionsAsync: async () => concedido,
  launchImageLibraryAsync: () => elegirArchivo("image/*"),
  launchCameraAsync: () => elegirArchivo("image/*"),
};

/* expo-notifications */
export const Notifications = {
  setNotificationHandler: () => {},
  requestPermissionsAsync: async () => concedido,
  getPermissionsAsync: async () => concedido,
  scheduleNotificationAsync: async ({ content = {}, trigger } = {}) => {
    const seg = trigger?.seconds ?? 0;
    console.log(`🔔 Notificación programada${seg ? ` en ${seg} s` : ""}: ${content.title ?? ""}`);
    setTimeout(() => console.log(`🔔 ${content.title ?? ""} — ${content.body ?? ""}`), Math.min(seg, 5) * 1000);
    return "notificacion-" + Date.now();
  },
  cancelAllScheduledNotificationsAsync: async () => {},
  getExpoPushTokenAsync: async () => ({ data: "ExponentPushToken[simulado]" }),
};

/* expo-camera */
export function useCameraPermissions() {
  const [p, setP] = useState({ granted: false, status: "undetermined" });
  return [p, async () => { setP(concedido); return concedido; }];
}
export function CameraView({ style, onBarcodeScanned, children }) {
  return h(Pressable, { style: [{ backgroundColor: "#111", alignItems: "center", justifyContent: "center", minHeight: 200 }, style], onPress: () => onBarcodeScanned?.({ type: "qr", data: "https://codigocamp.co" }) },
    h(Text, { style: { color: "#fff", textAlign: "center" } }, "📷 Cámara simulada\n(toca para leer un QR de ejemplo)"), children);
}
export const Camera = CameraView;

/* expo-font */
export const useFonts = () => [true, null];
export const Font = { loadAsync: async () => {} };

/* expo-splash-screen y expo-constants */
export const SplashScreen = { preventAutoHideAsync: async () => {}, hideAsync: async () => {} };
export const Constants = { expoConfig: { name: "Mi app", version: "1.0.0" }, appOwnership: "expo" };

/* @expo/vector-icons: dibuja un emoji parecido al ícono */
const EMOJI = { home: "🏠", search: "🔍", person: "👤", settings: "⚙️", heart: "❤️", star: "⭐", cart: "🛒", add: "➕", close: "✖️", trash: "🗑️", camera: "📷", "chevron-back": "‹", "chevron-forward": "›", menu: "☰", notifications: "🔔", mail: "✉️", call: "📞", location: "📍", time: "⏰", checkmark: "✔️", image: "🖼️", share: "📤", bookmark: "🔖", play: "▶️", pause: "⏸️" };
function crearIconos(familia) {
  return function Icono({ name = "", size = 24, color = "#111", style }) {
    const base = String(name).replace(/-(outline|sharp|circle|o)$/, "");
    return h(Text, { style: [{ fontSize: size * 0.85, color, lineHeight: size * 1.1 }, style], accessibilityLabel: `${familia} ${name}` }, EMOJI[name] ?? EMOJI[base] ?? "◆");
  };
}
export const Ionicons = crearIconos("Ionicons");
export const MaterialIcons = crearIconos("MaterialIcons");
export const MaterialCommunityIcons = crearIconos("MaterialCommunityIcons");
export const FontAwesome = crearIconos("FontAwesome");
export const FontAwesome5 = crearIconos("FontAwesome5");
export const Feather = crearIconos("Feather");
export const AntDesign = crearIconos("AntDesign");
export const Entypo = crearIconos("Entypo");

/* expo-router: lo justo para ver el ejemplo */
export function Link({ href, children, style, asChild }) {
  return h(Text, { style: [{ color: "#2563eb", textDecorationLine: "underline", marginVertical: 6 }, style], onPress: () => console.log("➡️ Expo Router iría a " + (typeof href === "string" ? href : href?.pathname)) }, children);
}
const NadaNav = Object.assign(() => null, { Screen: () => null });
export const Stack = NadaNav;
export const Tabs = NadaNav;
export const useRouter = () => ({ push: (r) => console.log("➡️ " + r), replace: (r) => console.log("➡️ " + r), back: () => console.log("⬅️ Atrás") });
export const router = useRouter();
export const useLocalSearchParams = () => ({});

/* react-native-gesture-handler: los gestos se simulan con toques */
export const GestureHandlerRootView = ({ style, children }) => h(View, { style: [{ flex: 1 }, style] }, children);
function gesto() {
  const g = { _fin: null, _act: null };
  for (const m of ["onBegin", "onStart", "onChange", "onFinalize", "minDistance", "activeOffsetX", "numberOfTaps", "enabled"]) g[m] = () => g;
  g.onUpdate = (f) => { g._act = f; return g; };
  g.onEnd = (f) => { g._fin = f; return g; };
  return g;
}
export const Gesture = { Pan: gesto, Tap: gesto, Pinch: gesto, LongPress: gesto, Fling: gesto };
export function GestureDetector({ gesture, children }) {
  // En la web: arrastra con el mouse o el dedo y al soltar se llama a onEnd con translationX/Y
  const [ini, setIni] = useState(null);
  return h(View, {
    onPointerDown: (e) => setIni({ x: e.nativeEvent.pageX, y: e.nativeEvent.pageY }),
    onPointerUp: (e) => { if (ini) gesture?._fin?.({ translationX: e.nativeEvent.pageX - ini.x, translationY: e.nativeEvent.pageY - ini.y }); setIni(null); },
  }, children);
}
