/* React Native en Aprende: el código se dibuja en un celular simulado con react-native-web.
   React Navigation, Expo y AsyncStorage se simulan con módulos propios (js/rn/) que imitan su API. */
const RV = '18.3.1';
const RNW = '0.19.13';
const ESM = (p) => `https://esm.sh/${p}`;

// Paquete → qué objeto de js/rn/expo.js expone y con qué nombres (para `import * as X` y `import X`)
export const PAQUETES_EXPO = {
  'expo-status-bar': { nombres: ['StatusBar'] },
  '@react-native-async-storage/async-storage': { obj: 'AsyncStorage', claves: ['getItem', 'setItem', 'removeItem', 'mergeItem', 'getAllKeys', 'multiGet', 'multiSet', 'clear'] },
  'expo-secure-store': { obj: 'SecureStore', claves: ['setItemAsync', 'getItemAsync', 'deleteItemAsync'] },
  'expo-haptics': { obj: 'Haptics', claves: ['ImpactFeedbackStyle', 'NotificationFeedbackType', 'impactAsync', 'notificationAsync', 'selectionAsync'] },
  'expo-location': { obj: 'Location', claves: ['Accuracy', 'requestForegroundPermissionsAsync', 'getForegroundPermissionsAsync', 'getCurrentPositionAsync', 'reverseGeocodeAsync'] },
  'expo-image-picker': { obj: 'ImagePicker', claves: ['MediaTypeOptions', 'requestMediaLibraryPermissionsAsync', 'requestCameraPermissionsAsync', 'launchImageLibraryAsync', 'launchCameraAsync'] },
  'expo-notifications': { obj: 'Notifications', claves: ['setNotificationHandler', 'requestPermissionsAsync', 'getPermissionsAsync', 'scheduleNotificationAsync', 'cancelAllScheduledNotificationsAsync', 'getExpoPushTokenAsync'] },
  'expo-camera': { nombres: ['CameraView', 'Camera', 'useCameraPermissions'] },
  'expo-font': { nombres: ['useFonts'], obj: 'Font', claves: ['loadAsync'] },
  'expo-splash-screen': { obj: 'SplashScreen', claves: ['preventAutoHideAsync', 'hideAsync'] },
  'expo-constants': { obj: 'Constants', claves: [] },
  '@expo/vector-icons': { nombres: ['Ionicons', 'MaterialIcons', 'MaterialCommunityIcons', 'FontAwesome', 'FontAwesome5', 'Feather', 'AntDesign', 'Entypo'] },
  'expo-router': { nombres: ['Link', 'Stack', 'Tabs', 'useRouter', 'router', 'useLocalSearchParams'] },
  'react-native-gesture-handler': { nombres: ['GestureHandlerRootView', 'Gesture', 'GestureDetector'] },
};
export const NAVEGACION = ['@react-navigation/native', '@react-navigation/native-stack', '@react-navigation/stack', '@react-navigation/bottom-tabs', '@react-navigation/drawer'];

const dataJS = (src) => 'data:text/javascript;charset=utf-8,' + encodeURIComponent(src);

/** Código del módulo que expone un paquete de Expo simulado con sus nombres reales. */
export function fuenteEnvoltorio({ nombres = [], obj, claves = [] }) {
  let s = `import * as E from "cc:expo";\n`;
  if (nombres.length) s += `export const { ${nombres.join(', ')} } = E;\n`;
  if (obj) {
    s += `const M = E.${obj};\nexport default M;\n`;
    if (claves.length) s += `export const { ${claves.join(', ')} } = M;\n`;
  } else if (nombres.length === 1) s += `export default E.${nombres[0]};\n`;
  return s;
}
const envoltorio = (d) => dataJS(fuenteEnvoltorio(d));

let mapaCache = null;
async function mapa() {
  if (mapaCache) return mapaCache;
  // El recuadro es de origen aislado: los módulos propios se pasan como data: para no depender de CORS
  const leer = async (r) => dataJS(await (await fetch(r)).text());
  const [rn, nav, expo] = await Promise.all(['/js/rn/react-native.js', '/js/rn/navegacion.js', '/js/rn/expo.js'].map(leer));
  const m = {
    'react': ESM(`react@${RV}`),
    'react/': ESM(`react@${RV}/`),
    'react-dom': ESM(`react-dom@${RV}?external=react`),
    'react-dom/client': ESM(`react-dom@${RV}/client?external=react`),
    'rnw': ESM(`react-native-web@${RNW}?external=react,react-dom`),
    'react-native': rn,
    'react-native-web': ESM(`react-native-web@${RNW}?external=react,react-dom`),
    'cc:nav': nav,
    'cc:expo': expo,
    'zustand': ESM('zustand@5.0.5?external=react'),
    'axios': ESM('axios@1.9.0'),
  };
  for (const p of NAVEGACION) m[p] = nav;
  for (const [p, d] of Object.entries(PAQUETES_EXPO)) m[p] = envoltorio(d);
  return (mapaCache = m);
}

/** Devuelve el código listo para el celular, o null si es un fragmento sin componente App que mostrar. */
export function prepararRN(code) {
  if (/AppRegistry\.(registerComponent|runApplication)/.test(code)) return code;
  if (!/\b(function|const|let|class)\s+App\b/.test(code)) return null;
  return code + '\nimport { AppRegistry as __ccAR } from "react-native";\n' +
    '__ccAR.registerComponent("main", () => App);\n__ccAR.runApplication("main", { rootTag: document.getElementById("root") });\n';
}

export const MENSAJE_FRAGMENTO = '📱 Este ejemplo es un fragmento (no tiene un componente App), así que no hay pantalla que dibujar.\n\n' +
  'Léelo con calma y, para probarlo completo, llévalo a Trabajo: crea un proyecto de Expo y ejecuta «npx expo start» (o «expo start») para abrirlo en tu celular con Expo Go.';

export async function paginaRN(js) {
  const imports = await mapa();
  const consola = `<script>(()=>{window.process=window.process||{env:{NODE_ENV:"development"}};` +
    `window.require=(r)=>/\\.(png|jpe?g|gif|webp|svg)$/i.test(r)?{uri:"data:image/svg+xml,"+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96"><rect width="96" height="96" rx="20" fill="#7c3aed"/><text x="48" y="60" font-size="40" text-anchor="middle" fill="#fff">🖼</text></svg>')}:r;` +
    `const caja=()=>document.getElementById("cc-consola");const fmt=a=>a.map(x=>{if(x instanceof Error)return x.message;try{return typeof x==="object"?JSON.stringify(x):String(x)}catch{return String(x)}}).join(" ");` +
    `const poner=(t,err)=>{const c=caja();if(!c)return;c.hidden=false;const l=document.createElement("div");l.textContent=t;if(err)l.className="e";c.appendChild(l);c.scrollTop=c.scrollHeight};` +
    `const log=console.log.bind(console);console.log=(...a)=>{log(...a);poner(fmt(a))};` +
    `const er=console.error.bind(console);console.error=(...a)=>{er(...a);const s=String(a[0]);if(!/^Warning:|The above error occurred|Consider adding an error boundary|useNativeDriver|Animated:/.test(s))poner(fmt(a),1)};` +
    `const wa=console.warn.bind(console);console.warn=(...a)=>{wa(...a)};` +
    `addEventListener("error",e=>poner("Error: "+(e.message||e.error),1));addEventListener("unhandledrejection",e=>poner("Error: "+(e.reason?.message||e.reason),1));})()<\/script>`;
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<style>html,body{margin:0;height:100%;background:#e2e8f0;font-family:system-ui,sans-serif}` +
    `.cel{position:relative;width:min(340px,94vw);height:min(600px,86vh);margin:14px auto 6px;border:10px solid #111827;border-radius:36px;background:#fff;overflow:hidden;box-shadow:0 12px 30px rgba(0,0,0,.25);display:flex;flex-direction:column}` +
    `.barra{height:22px;flex:none;display:flex;justify-content:space-between;align-items:center;padding:0 18px;font:600 11px system-ui;color:#111;background:#fff}` +
    `.barra i{width:70px;height:16px;background:#111827;border-radius:0 0 12px 12px;margin-top:-6px}` +
    `#root{flex:1;display:flex;flex-direction:column;position:relative;overflow:hidden}#root>div{flex:1}` +
    `#cc-consola{font:12px ui-monospace,monospace;background:#0f172a;color:#e2e8f0;padding:6px 8px;border-radius:8px;margin:6px auto 12px;width:min(340px,94vw);box-sizing:border-box;max-height:120px;overflow:auto}#cc-consola::before{content:"Consola";display:block;color:#94a3b8;margin-bottom:2px}#cc-consola .e{color:#fca5a5}</style>` +
    `<script type="importmap">${JSON.stringify({ imports })}<\/script>${consola}</head><body>` +
    `<div class="cel"><div class="barra"><span>9:41</span><i></i><span>📶 🔋</span></div><div id="root"></div></div><div id="cc-consola" hidden></div>` +
    `<script type="module">${js.replace(/<\/script/gi, '<\\/script')}<\/script></body></html>`;
}
