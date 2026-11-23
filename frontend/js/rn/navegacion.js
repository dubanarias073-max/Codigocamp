// React Navigation simplificado para el celular simulado de Aprende.
// Mismos nombres que la librería real: NavigationContainer, createNativeStackNavigator,
// createBottomTabNavigator, createDrawerNavigator, useNavigation, useRoute...
import React, { createContext, useContext, useEffect, useState } from "react";
import { Pressable, Text, View } from "react-native";

const h = React.createElement;
const Ctx = createContext(null);

export const DefaultTheme = { dark: false, colors: { primary: "#007aff", background: "#f2f2f2", card: "#fff", text: "#1c1c1e", border: "#d8d8d8", notification: "#ff3b30" } };
export const DarkTheme = { dark: true, colors: { primary: "#0a84ff", background: "#010101", card: "#121212", text: "#e5e5e7", border: "#272729", notification: "#ff453a" } };

export function NavigationContainer({ children }) {
  return h(View, { style: { flex: 1 } }, children);
}
export const useNavigation = () => {
  const c = useContext(Ctx);
  if (!c) throw new Error("useNavigation solo funciona dentro de una pantalla de un Navigator");
  return c.navigation;
};
export const useRoute = () => useContext(Ctx)?.route;
export const useIsFocused = () => true;
export const useFocusEffect = (fn) => useEffect(() => fn(), [fn]);

const Screen = () => null;
const Group = ({ children }) => children;

function pantallas(children) {
  const out = [];
  React.Children.forEach(children, (c) => {
    if (!c || !c.props) return;
    if (c.type === Group) out.push(...pantallas(c.props.children));
    else if (c.props.name) out.push(c.props);
  });
  return out;
}

function opciones(def, route, navigation, comunes, extra) {
  const o = typeof def.options === "function" ? def.options({ route, navigation }) : def.options;
  const s = typeof comunes === "function" ? comunes({ route, navigation }) : comunes;
  return { ...s, ...o, ...extra };
}

function contenido(def, route, navigation) {
  const C = def.component;
  if (C) return h(C, { navigation, route });
  if (typeof def.children === "function") return def.children({ navigation, route });
  return null;
}

function Encabezado({ op, titulo, atras, izquierda }) {
  if (op.headerShown === false) return null;
  const color = op.headerTintColor ?? "#111";
  return h(View, { style: [{ height: 52, flexDirection: "row", alignItems: "center", paddingHorizontal: 12, backgroundColor: "#fff", borderBottomWidth: 1, borderColor: "#e5e7eb" }, op.headerStyle] },
    izquierda ?? (atras ? h(Pressable, { onPress: atras, style: { paddingRight: 10 } }, h(Text, { style: { fontSize: 26, color } }, "‹")) : null),
    h(Text, { style: [{ fontSize: 17, fontWeight: "600", color, flex: 1 }, op.headerTitleStyle], numberOfLines: 1 }, op.headerTitle && typeof op.headerTitle === "string" ? op.headerTitle : titulo),
    op.headerRight ? op.headerRight({ tintColor: color }) : null);
}

function crearStack() {
  function Navigator({ children, screenOptions, initialRouteName }) {
    const lista = pantallas(children);
    const inicial = lista.find((s) => s.name === initialRouteName) ?? lista[0];
    const [pila, setPila] = useState([{ name: inicial?.name, params: inicial?.initialParams }]);
    const [extra, setExtra] = useState({});
    if (!lista.length) return h(Text, null, "El Navigator no tiene pantallas");
    const actual = pila[pila.length - 1];
    const def = lista.find((s) => s.name === actual.name) ?? lista[0];
    const existe = (n) => lista.some((s) => s.name === n) || (console.error(`No hay ninguna pantalla llamada "${n}". Revisa el name de Stack.Screen.`), false);
    const navigation = {
      navigate: (name, params) => existe(name) && setPila((p) => {
        const i = p.findIndex((x) => x.name === name);
        return i >= 0 ? [...p.slice(0, i), { name, params: params ?? p[i].params }] : [...p, { name, params }];
      }),
      push: (name, params) => existe(name) && setPila((p) => [...p, { name, params }]),
      replace: (name, params) => existe(name) && setPila((p) => [...p.slice(0, -1), { name, params }]),
      goBack: () => setPila((p) => (p.length > 1 ? p.slice(0, -1) : p)),
      popToTop: () => setPila((p) => [p[0]]),
      canGoBack: () => pila.length > 1,
      setParams: (pr) => setPila((p) => [...p.slice(0, -1), { ...p[p.length - 1], params: { ...p[p.length - 1].params, ...pr } }]),
      setOptions: (o) => setExtra((e) => ({ ...e, [actual.name]: { ...e[actual.name], ...o } })),
    };
    const route = { key: actual.name + "-" + pila.length, name: actual.name, params: actual.params };
    const op = opciones(def, route, navigation, screenOptions, extra[actual.name]);
    return h(Ctx.Provider, { value: { navigation, route } },
      h(View, { style: { flex: 1 } },
        h(Encabezado, { op, titulo: op.title ?? actual.name, atras: pila.length > 1 ? navigation.goBack : null }),
        h(View, { style: [{ flex: 1 }, op.contentStyle] }, contenido(def, route, navigation))));
  }
  return { Navigator, Screen, Group };
}

function crearTabs() {
  function Navigator({ children, screenOptions, initialRouteName }) {
    const lista = pantallas(children);
    const [i, setI] = useState(Math.max(0, lista.findIndex((s) => s.name === initialRouteName)));
    const [params, setParams] = useState({});
    if (!lista.length) return h(Text, null, "El Navigator no tiene pantallas");
    const def = lista[i] ?? lista[0];
    const navigation = {
      navigate: (name, p) => { const j = lista.findIndex((s) => s.name === name); if (j < 0) return console.error(`No hay ninguna pestaña llamada "${name}".`); setI(j); if (p) setParams((x) => ({ ...x, [name]: p })); },
      goBack: () => setI(0), canGoBack: () => i > 0, setOptions: () => {}, setParams: () => {},
    };
    const route = { key: def.name, name: def.name, params: params[def.name] ?? def.initialParams };
    const op = opciones(def, route, navigation, screenOptions);
    const activo = op.tabBarActiveTintColor ?? "#007aff", inactivo = op.tabBarInactiveTintColor ?? "#8e8e93";
    return h(Ctx.Provider, { value: { navigation, route } },
      h(View, { style: { flex: 1 } },
        h(Encabezado, { op, titulo: op.title ?? def.name }),
        h(View, { style: { flex: 1 } }, contenido(def, route, navigation)),
        h(View, { style: [{ flexDirection: "row", borderTopWidth: 1, borderColor: "#e5e7eb", backgroundColor: "#fff", paddingVertical: 6 }, op.tabBarStyle] },
          lista.map((s, j) => {
            const o = opciones(s, { name: s.name }, navigation, screenOptions);
            const color = j === i ? activo : inactivo;
            return h(Pressable, { key: s.name, onPress: () => setI(j), style: { flex: 1, alignItems: "center", gap: 2 } },
              o.tabBarIcon ? o.tabBarIcon({ focused: j === i, color, size: 22 }) : h(Text, { style: { fontSize: 18, color } }, "●"),
              h(Text, { style: { fontSize: 11, color } }, o.tabBarLabel ?? o.title ?? s.name),
              o.tabBarBadge != null ? h(Text, { style: { position: "absolute", top: -2, right: "30%", backgroundColor: "#ff3b30", color: "#fff", fontSize: 10, borderRadius: 8, paddingHorizontal: 4 } }, String(o.tabBarBadge)) : null);
          }))));
  }
  return { Navigator, Screen, Group };
}

function crearDrawer() {
  function Navigator({ children, screenOptions, initialRouteName }) {
    const lista = pantallas(children);
    const [i, setI] = useState(Math.max(0, lista.findIndex((s) => s.name === initialRouteName)));
    const [abierto, setAbierto] = useState(false);
    if (!lista.length) return h(Text, null, "El Navigator no tiene pantallas");
    const def = lista[i] ?? lista[0];
    const navigation = {
      navigate: (name) => { const j = lista.findIndex((s) => s.name === name); if (j < 0) return console.error(`No hay ninguna pantalla llamada "${name}".`); setI(j); setAbierto(false); },
      openDrawer: () => setAbierto(true), closeDrawer: () => setAbierto(false), toggleDrawer: () => setAbierto((a) => !a),
      goBack: () => setI(0), canGoBack: () => false, setOptions: () => {},
    };
    const route = { key: def.name, name: def.name, params: def.initialParams };
    const op = opciones(def, route, navigation, screenOptions);
    const boton = h(Pressable, { onPress: () => setAbierto(true), style: { paddingRight: 12 } }, h(Text, { style: { fontSize: 22, color: op.headerTintColor ?? "#111" } }, "☰"));
    return h(Ctx.Provider, { value: { navigation, route } },
      h(View, { style: { flex: 1 } },
        h(Encabezado, { op, titulo: op.title ?? def.name, izquierda: boton }),
        h(View, { style: { flex: 1 } }, contenido(def, route, navigation)),
        abierto ? h(Pressable, { onPress: () => setAbierto(false), style: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,.35)" } }) : null,
        abierto ? h(View, { style: { position: "absolute", top: 0, bottom: 0, left: 0, width: "72%", backgroundColor: "#fff", paddingTop: 30 } },
          lista.map((s, j) => h(Pressable, { key: s.name, onPress: () => navigation.navigate(s.name), style: { padding: 14, backgroundColor: j === i ? "#e0e7ff" : "transparent" } },
            h(Text, { style: { fontSize: 15, fontWeight: j === i ? "700" : "400" } }, s.options?.title ?? s.name)))) : null));
  }
  return { Navigator, Screen, Group };
}

export const createNativeStackNavigator = crearStack;
export const createStackNavigator = crearStack;
export const createBottomTabNavigator = crearTabs;
export const createDrawerNavigator = crearDrawer;
