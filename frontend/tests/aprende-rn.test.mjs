// React Native en Aprende: preparación del código y módulos simulados de Expo
import { test } from "node:test";
import assert from "node:assert/strict";
import { prepararRN, PAQUETES_EXPO, fuenteEnvoltorio } from "../js/aprende-rn.js";

test("prepararRN registra App con AppRegistry", () => {
  const c = prepararRN('import { Text } from "react-native";\nexport default function App() { return <Text>Hola</Text>; }');
  assert.match(c, /registerComponent\("main", \(\) => App\)/);
  assert.match(c, /runApplication\("main"/);
});

test("prepararRN deja igual el código que ya registra la app", () => {
  const codigo = 'AppRegistry.registerComponent("x", () => Otra);';
  assert.equal(prepararRN(codigo), codigo);
});

test("un fragmento sin App no se dibuja", () => {
  assert.equal(prepararRN('navigation.navigate("Perfil");'), null);
});

test("los paquetes de Expo exponen sus nombres reales", () => {
  const s = fuenteEnvoltorio(PAQUETES_EXPO["@react-native-async-storage/async-storage"]);
  assert.match(s, /export default M/);
  assert.match(s, /getItem, setItem/);
  assert.match(fuenteEnvoltorio(PAQUETES_EXPO["expo-status-bar"]), /export default E\.StatusBar/);
});
