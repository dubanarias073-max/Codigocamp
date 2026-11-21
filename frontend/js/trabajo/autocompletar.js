// Autocompletado de Trabajo, como en VS Code: mientras escribes aparece una lista de sugerencias y con Enter (o Tab)
// se inserta la elegida. Sirve para los dos editores:
//   · Monaco (el de VS Code): ya trae IntelliSense de JavaScript/TypeScript, HTML, CSS y JSON. Aquí se le suma lo que le
//     falta: Python, Java, C/C++, C#, PHP, SQL, Go, Rust, Ruby, Kotlin, Swift y Bash (palabras clave, funciones,
//     módulos, métodos después del punto, nombres de tu proyecto), fragmentos (def, for, main, sout, log…) y Emmet en
//     HTML (`!`, `ul>li*3`, `div.caja#id`…).
//   · El editor simple (si Monaco no carga): misma lista de sugerencias en un menú propio.
// No usa la red ni la IA: todo se calcula en el navegador al instante.

const lista = (s) => s.trim().split(/\s+/);

// --------------------------------------------------------------------------------- lenguajes ----
const FAMILIA = {
  py: "py", pyw: "py", js: "js", mjs: "js", cjs: "js", jsx: "js", ts: "js", tsx: "js", mts: "js", vue: "html",
  html: "html", htm: "html", css: "css", scss: "css", less: "css", java: "java", c: "c", h: "c", cpp: "c", cc: "c", hpp: "c",
  cs: "cs", php: "php", sql: "sql", go: "go", rs: "rs", rb: "rb", kt: "kt", swift: "swift", sh: "sh", bash: "sh",
};
export const familiaDe = (ext) => FAMILIA[(ext || "").toLowerCase()] ?? null;
/** Id de lenguaje de Monaco -> familia. */
export const FAMILIA_MONACO = { python: "py", java: "java", c: "c", cpp: "c", csharp: "cs", php: "php", sql: "sql", go: "go", rust: "rs",
  ruby: "rb", kotlin: "kt", swift: "swift", shell: "sh", javascript: "js", typescript: "js", html: "html", css: "css", scss: "css", less: "css" };

// Fragmentos: [atajo, descripción, cuerpo]. El cuerpo usa la sintaxis de VS Code: ${1:texto}, $0, \t = una sangría.
const S = (atajo, desc, cuerpo) => ({ atajo, desc, cuerpo });

const PY = {
  kw: lista("False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield match case self"),
  fn: lista("print( input( len( range( int( str( float( bool( list( dict( set( tuple( open( enumerate( zip( map( filter( sorted( reversed( sum( min( max( abs( round( type( isinstance( super() any( all( chr( ord( format( id( iter( next( divmod( pow( hex( bin( oct( hash( repr( vars( dir( getattr( setattr( hasattr( exit() help( Exception( ValueError( TypeError( KeyError( IndexError( ZeroDivisionError( FileNotFoundError( __name__ __init__ __str__ __repr__"),
  modulos: lista("os sys math random json datetime time re collections itertools functools pathlib csv sqlite3 typing dataclasses string statistics turtle tkinter flask requests pymysql mysql.connector unittest numpy pandas matplotlib.pyplot hashlib base64 uuid shutil subprocess threading asyncio socket urllib.request http.server decimal fractions copy pprint textwrap getpass"),
  miembros: {
    math: "pi e tau inf nan sqrt( pow( floor( ceil( fabs( factorial( gcd( lcm( log( log10( log2( exp( sin( cos( tan( asin( acos( atan( atan2( degrees( radians( hypot( isclose( comb( perm( prod( trunc( isqrt(",
    random: "random() randint( choice( choices( shuffle( sample( uniform( seed( randrange( gauss(",
    os: "path getcwd() listdir( mkdir( makedirs( remove( rename( rmdir( environ getenv( system( walk( sep chdir( name",
    "os.path": "join( exists( isfile( isdir( basename( dirname( abspath( splitext( getsize( expanduser(",
    json: "dumps( loads( dump( load( JSONDecodeError",
    datetime: "datetime date time timedelta( timezone",
    "datetime.datetime": "now() today() strptime( strftime( fromisoformat( utcnow()",
    "datetime.date": "today() fromisoformat(",
    time: "time() sleep( strftime( localtime() perf_counter() monotonic()",
    sys: "argv exit( path version platform stdin stdout stderr getsizeof( setrecursionlimit(",
    re: "match( search( findall( sub( split( compile( fullmatch( finditer( escape( IGNORECASE MULTILINE DOTALL",
    sqlite3: "connect( Row Error IntegrityError OperationalError",
    string: "ascii_letters ascii_lowercase ascii_uppercase digits punctuation whitespace",
    statistics: "mean( median( mode( stdev( variance( pstdev(",
    collections: "Counter( defaultdict( OrderedDict( deque( namedtuple(",
    itertools: "count( cycle( repeat( chain( combinations( permutations( product( groupby( accumulate( islice(",
    functools: "reduce( partial( lru_cache( cache wraps(",
    pathlib: "Path(",
    csv: "reader( writer( DictReader( DictWriter(",
    typing: "List Dict Optional Tuple Union Any Callable Set Iterable",
    dataclasses: "dataclass field( asdict(",
    "mysql.connector": "connect( Error",
    pymysql: "connect( cursors",
    turtle: "Turtle() Screen() forward( backward( left( right( penup() pendown() color( speed( done() circle( goto( shape( bgcolor( pensize( begin_fill() end_fill() hideturtle()",
    tkinter: "Tk() Label( Button( Entry( Frame( Text( Canvas( messagebox StringVar() IntVar() END mainloop() Toplevel( Listbox( Scrollbar(",
    flask: "Flask( render_template( request redirect( url_for( jsonify( session abort( flash( Blueprint( send_file(",
    requests: "get( post( put( delete( patch( Session()",
    numpy: "array( arange( zeros( ones( linspace( mean( sum( max( min( sqrt( random reshape( dot( std( median( where( concatenate(",
    pandas: "DataFrame( Series( read_csv( read_excel( read_json( concat( merge( to_datetime(",
    "matplotlib.pyplot": "plot( show() title( xlabel( ylabel( bar( scatter( hist( pie( legend() figure( subplots( savefig( grid(",
    hashlib: "sha256( md5( sha1(",
    uuid: "uuid4()",
    shutil: "copy( copytree( move( rmtree(",
    subprocess: "run( Popen( check_output(",
    unittest: "TestCase main()",
  },
  metodos: lista(`upper() lower() strip() lstrip() rstrip() split( join( replace( find( index( count( startswith( endswith( format( isdigit() isalpha() isalnum() isupper() islower() title() capitalize() zfill( center( ljust( rjust( encode( decode(
    append( extend( insert( remove( pop( clear() sort( reverse() copy()
    keys() values() items() get( update( setdefault( popitem()
    add( discard( union( intersection( difference(
    read() readline() readlines() write( writelines( close()
    execute( executemany( fetchall() fetchone() fetchmany( commit() cursor() rollback() lastrowid rowcount`),
  snip: [
    S("def", "Función", "def ${1:nombre}(${2}):\n\t${0:pass}"),
    S("class", "Clase con constructor", "class ${1:Nombre}:\n\tdef __init__(self${2:, valor}):\n\t\t${0:self.valor = valor}"),
    S("if", "Condición if", "if ${1:condicion}:\n\t${0:pass}"),
    S("ifelse", "if / else", "if ${1:condicion}:\n\t${2:pass}\nelse:\n\t${0:pass}"),
    S("elif", "elif", "elif ${1:condicion}:\n\t${0:pass}"),
    S("for", "Ciclo for", "for ${1:elemento} in ${2:lista}:\n\t${0:pass}"),
    S("forr", "for con range", "for ${1:i} in range(${2:10}):\n\t${0:pass}"),
    S("fore", "for con enumerate", "for ${1:i}, ${2:valor} in enumerate(${3:lista}):\n\t${0:pass}"),
    S("while", "Ciclo while", "while ${1:condicion}:\n\t${0:pass}"),
    S("try", "try / except", "try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${0:print(e)}"),
    S("with", "Abrir un archivo", "with open(${1:\"archivo.txt\"}, ${2:\"r\"}, encoding=\"utf-8\") as ${3:f}:\n\t${0:contenido = f.read()}"),
    S("main", "if __name__ == \"__main__\"", "if __name__ == \"__main__\":\n\t${0:main()}"),
    S("lambda", "Función lambda", "lambda ${1:x}: ${0:x}"),
    S("lc", "Lista por comprensión", "[${1:x} for ${2:x} in ${3:lista}${4: if ${5:condicion}}]"),
    S("inputint", "Pedir un número", "${1:numero} = int(input(\"${2:Escribe un número: }\"))"),
    S("printf", "print con f-string", "print(f\"${1:texto} {${2:variable}}\")"),
    S("sqlite", "Conectar a SQLite", "import sqlite3\n\nconexion = sqlite3.connect(\"${1:datos.db}\")\ncursor = conexion.cursor()\ncursor.execute(\"${2:SELECT * FROM tabla}\")\n${0:filas = cursor.fetchall()}\nconexion.close()"),
    S("mysql", "Conectar a MySQL (XAMPP)", "import pymysql\n\nconexion = pymysql.connect(host=\"localhost\", user=\"root\", password=\"\", database=\"${1:mi_base}\")\ncursor = conexion.cursor()\ncursor.execute(\"${2:SELECT * FROM tabla}\")\n${0:filas = cursor.fetchall()}\nconexion.close()"),
    S("flask", "App de Flask", "from flask import Flask, render_template, request\n\napp = Flask(__name__)\n\n\n@app.route(\"/\")\ndef inicio():\n\treturn ${0:\"¡Hola, mundo!\"}\n\n\nif __name__ == \"__main__\":\n\tapp.run(debug=True)"),
    S("route", "Ruta de Flask", "@app.route(\"/${1:ruta}\"${2:, methods=[\"GET\", \"POST\"]})\ndef ${3:vista}():\n\t${0:return \"\"}"),
  ],
};

const JS = {
  kw: lista("break case catch class const continue debugger default delete do else export extends false finally for function if import in instanceof let new null return super switch this throw true try typeof undefined var void while with yield async await of static get set"),
  fn: lista("console document window Math JSON Array Object String Number Boolean Date Promise Map Set fetch( setTimeout( setInterval( clearTimeout( clearInterval( parseInt( parseFloat( isNaN( alert( prompt( confirm( localStorage sessionStorage Error( requestAnimationFrame( structuredClone("),
  miembros: {
    console: "log( error( warn( info( table( clear() group( groupEnd() time( timeEnd(",
    document: "getElementById( querySelector( querySelectorAll( createElement( addEventListener( body head title cookie documentElement createTextNode(",
    Math: "random() floor( ceil( round( max( min( abs( sqrt( pow( PI trunc( sign(",
    JSON: "parse( stringify(",
    Object: "keys( values( entries( assign( freeze( fromEntries(",
    Array: "from( isArray( of(",
    localStorage: "getItem( setItem( removeItem( clear()",
    sessionStorage: "getItem( setItem( removeItem( clear()",
    window: "location addEventListener( innerWidth innerHeight scrollTo( open( alert(",
    Promise: "all( race( resolve( reject( allSettled(",
    Number: "parseInt( parseFloat( isInteger( MAX_SAFE_INTEGER",
  },
  metodos: lista(`length push( pop() shift() unshift( map( filter( forEach( reduce( find( findIndex( some( every( includes( indexOf( join( split( slice( splice( concat( sort( reverse() at( flat() fill(
    toUpperCase() toLowerCase() trim() startsWith( endsWith( replace( replaceAll( padStart( repeat( charAt( toFixed( toString()
    then( catch( finally( json() text() ok status
    addEventListener( removeEventListener( textContent innerHTML innerText value classList style appendChild( append( remove() setAttribute( getAttribute( querySelector( querySelectorAll( closest( dataset focus() click() checked disabled hidden
    add( toggle( contains( has( get( set( delete( keys() values() entries() size`),
  snip: [
    S("log", "console.log()", "console.log(${0});"),
    S("clg", "console.log()", "console.log(${0});"),
    S("fn", "Función", "function ${1:nombre}(${2}) {\n\t${0}\n}"),
    S("afn", "Función flecha", "const ${1:nombre} = (${2}) => {\n\t${0}\n};"),
    S("asyncfn", "Función async", "async function ${1:nombre}(${2}) {\n\t${0}\n}"),
    S("if", "Condición if", "if (${1:condicion}) {\n\t${0}\n}"),
    S("ifelse", "if / else", "if (${1:condicion}) {\n\t${2}\n} else {\n\t${0}\n}"),
    S("for", "Ciclo for", "for (let ${1:i} = 0; ${1:i} < ${2:lista}.length; ${1:i}++) {\n\t${0}\n}"),
    S("forof", "for…of", "for (const ${1:elemento} of ${2:lista}) {\n\t${0}\n}"),
    S("forin", "for…in", "for (const ${1:clave} in ${2:objeto}) {\n\t${0}\n}"),
    S("foreach", "forEach", "${1:lista}.forEach((${2:elemento}) => {\n\t${0}\n});"),
    S("while", "Ciclo while", "while (${1:condicion}) {\n\t${0}\n}"),
    S("switch", "switch", "switch (${1:valor}) {\n\tcase ${2:1}:\n\t\t${3}\n\t\tbreak;\n\tdefault:\n\t\t${0}\n}"),
    S("try", "try / catch", "try {\n\t${1}\n} catch (${2:error}) {\n\t${0:console.error(error);}\n}"),
    S("class", "Clase", "class ${1:Nombre} {\n\tconstructor(${2}) {\n\t\t${0}\n\t}\n}"),
    S("imp", "import", "import ${2:nombre} from \"${1:modulo}\";"),
    S("imd", "import { }", "import { ${2} } from \"${1:modulo}\";"),
    S("fetch", "fetch con await", "const ${1:respuesta} = await fetch(\"${2:url}\");\nconst ${3:datos} = await ${1:respuesta}.json();$0"),
    S("timeout", "setTimeout", "setTimeout(() => {\n\t${0}\n}, ${1:1000});"),
    S("interval", "setInterval", "setInterval(() => {\n\t${0}\n}, ${1:1000});"),
    S("qs", "document.querySelector", "document.querySelector(\"${1}\")$0"),
    S("gid", "document.getElementById", "document.getElementById(\"${1}\")$0"),
    S("ael", "addEventListener", "${1:elemento}.addEventListener(\"${2:click}\", (${3:e}) => {\n\t${0}\n});"),
  ],
};

const HTML_TAGS = lista("a abbr address article aside audio b blockquote body br button canvas caption code col dialog details div dl dt dd em fieldset figure figcaption footer form h1 h2 h3 h4 h5 h6 head header hr html i iframe img input label legend li link main mark meta nav noscript ol optgroup option output p picture pre progress q script section select small source span strong style sub summary sup table tbody td template textarea tfoot th thead time title tr u ul video");
const HTML_VACIAS = new Set(lista("area base br col embed hr img input link meta source track wbr"));
const HTML = {
  kw: [],
  fn: [],
  snip: [
    S("!", "Página HTML completa", "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n\t<meta charset=\"UTF-8\">\n\t<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n\t<title>${1:Documento}</title>\n\t<link rel=\"stylesheet\" href=\"${2:style.css}\">\n</head>\n<body>\n\t$0\n\t<script src=\"${3:script.js}\"></script>\n</body>\n</html>"),
    S("html:5", "Página HTML completa", "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n\t<meta charset=\"UTF-8\">\n\t<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n\t<title>${1:Documento}</title>\n</head>\n<body>\n\t$0\n</body>\n</html>"),
    S("link:css", "Enlazar CSS", "<link rel=\"stylesheet\" href=\"${1:style.css}\">"),
    S("script:src", "Enlazar JavaScript", "<script src=\"${1:script.js}\"></script>"),
    S("a:link", "Enlace", "<a href=\"${1:https://}\">${0}</a>"),
    S("img", "Imagen", "<img src=\"${1}\" alt=\"${2}\">"),
    S("input:text", "Campo de texto", "<input type=\"text\" name=\"${1}\" id=\"${2:$1}\" placeholder=\"${3}\">"),
    S("input:password", "Campo de contraseña", "<input type=\"password\" name=\"${1:contrasena}\" id=\"${2:$1}\">"),
    S("input:email", "Campo de correo", "<input type=\"email\" name=\"${1:correo}\" id=\"${2:$1}\">"),
    S("form:post", "Formulario", "<form action=\"${1}\" method=\"post\">\n\t$0\n</form>"),
    S("btn", "Botón", "<button type=\"${1:button}\">${0:Enviar}</button>"),
    S("table", "Tabla", "<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>${1:Columna}</th>\n\t\t</tr>\n\t</thead>\n\t<tbody>\n\t\t<tr>\n\t\t\t<td>${0}</td>\n\t\t</tr>\n\t</tbody>\n</table>"),
  ],
};

const CSS = {
  kw: lista("display flex grid block inline-block none position relative absolute fixed sticky color background background-color margin padding border border-radius width height max-width min-height font-size font-weight font-family text-align justify-content align-items gap flex-direction flex-wrap grid-template-columns box-shadow transition transform opacity overflow cursor z-index top left right bottom line-height text-decoration center space-between space-around column row wrap auto bold solid hover"),
  fn: [],
  snip: [
    S("flexc", "Centrar con flex", "display: flex;\njustify-content: center;\nalign-items: center;$0"),
    S("grid3", "Rejilla de 3 columnas", "display: grid;\ngrid-template-columns: repeat(${1:3}, 1fr);\ngap: ${2:16px};$0"),
    S("media", "@media (celular)", "@media (max-width: ${1:700px}) {\n\t$0\n}"),
    S("reset", "Reinicio básico", "* {\n\tmargin: 0;\n\tpadding: 0;\n\tbox-sizing: border-box;\n}$0"),
  ],
};

const JAVA = {
  kw: lista("abstract assert boolean break byte case catch char class const continue default do double else enum extends final finally float for if implements import instanceof int interface long native new null package private protected public return short static super switch synchronized this throw throws transient try void volatile while var true false record"),
  fn: lista("String System Scanner ArrayList HashMap HashSet LinkedList List Map Set Math Integer Double Boolean Character Arrays Collections Random LocalDate Object Exception RuntimeException StringBuilder Thread Optional"),
  miembros: {
    System: "out in err exit( currentTimeMillis() nanoTime() lineSeparator()",
    "System.out": "println( print( printf(",
    Math: "random() max( min( abs( pow( sqrt( round( floor( ceil( PI",
    Integer: "parseInt( valueOf( MAX_VALUE MIN_VALUE toString(",
    Double: "parseDouble( valueOf(",
    String: "valueOf( format( join(",
    Arrays: "sort( toString( asList( fill( copyOf(",
    Collections: "sort( reverse( max( min( shuffle(",
  },
  metodos: lista(`length() charAt( equals( equalsIgnoreCase( substring( indexOf( contains( toUpperCase() toLowerCase() trim() split( replace( isEmpty() startsWith( endsWith( compareTo(
    nextInt() nextLine() next() nextDouble() nextBoolean() hasNext() hasNextInt() close()
    add( get( set( remove( size() contains( clear() isEmpty() put( containsKey( keySet() values() entrySet() getOrDefault( forEach( stream()
    append( toString() reverse() length`),
  snip: [
    S("main", "public static void main", "public static void main(String[] args) {\n\t${0}\n}"),
    S("psvm", "public static void main", "public static void main(String[] args) {\n\t${0}\n}"),
    S("sout", "System.out.println()", "System.out.println(${0});"),
    S("souf", "System.out.printf()", "System.out.printf(\"${1:%s}%n\", ${0});"),
    S("class", "Clase", "public class ${1:Nombre} {\n\t${0}\n}"),
    S("fori", "for con índice", "for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${0}\n}"),
    S("foreach", "for-each", "for (${1:String} ${2:elemento} : ${3:lista}) {\n\t${0}\n}"),
    S("if", "if", "if (${1:condicion}) {\n\t${0}\n}"),
    S("ifelse", "if / else", "if (${1:condicion}) {\n\t${2}\n} else {\n\t${0}\n}"),
    S("while", "while", "while (${1:condicion}) {\n\t${0}\n}"),
    S("try", "try / catch", "try {\n\t${1}\n} catch (${2:Exception} e) {\n\t${0:e.printStackTrace();}\n}"),
    S("scanner", "Leer del teclado", "Scanner ${1:sc} = new Scanner(System.in);$0"),
    S("metodo", "Método", "public ${1:void} ${2:nombre}(${3}) {\n\t${0}\n}"),
  ],
};

const C = {
  kw: lista("auto break case char const continue default do double else enum extern float for goto if int long register return short signed sizeof static struct switch typedef union unsigned void volatile while bool true false nullptr class public private protected namespace using template typename new delete std string vector cout cin endl include"),
  fn: lista("printf( scanf( puts( gets( malloc( free( strlen( strcpy( strcmp( strcat( fopen( fclose( fprintf( fgets( atoi( rand() srand( time( abs( sqrt( pow( exit("),
  miembros: { std: "cout cin endl string vector map set sort( swap( max( min( getline(" },
  metodos: lista("push_back( pop_back() size() begin() end() empty() clear() at( length() substr( find( insert( erase( front() back()"),
  snip: [
    S("main", "int main()", "int main() {\n\t${0}\n\treturn 0;\n}"),
    S("include", "#include", "#include <${1:stdio.h}>$0"),
    S("printf", "printf()", "printf(\"${1:%d}\\n\"${2:, valor});$0"),
    S("scanf", "scanf()", "scanf(\"${1:%d}\", &${2:valor});$0"),
    S("cout", "std::cout", "std::cout << ${1} << std::endl;$0"),
    S("cin", "std::cin", "std::cin >> ${1};$0"),
    S("for", "for", "for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${0}\n}"),
    S("if", "if", "if (${1:condicion}) {\n\t${0}\n}"),
    S("while", "while", "while (${1:condicion}) {\n\t${0}\n}"),
    S("struct", "struct", "struct ${1:Nombre} {\n\t${0}\n};"),
  ],
};

const CS = {
  kw: lista("abstract as base bool break byte case catch char checked class const continue decimal default delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long namespace new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while var async await get set"),
  fn: lista("Console Math String List Dictionary Convert int.Parse( DateTime Random Exception Task"),
  miembros: { Console: "WriteLine( Write( ReadLine() ReadKey() Clear()", Math: "Max( Min( Abs( Pow( Sqrt( Round( Floor( Ceiling( PI", Convert: "ToInt32( ToDouble( ToString( ToBoolean(" },
  metodos: lista("Add( Remove( Count Contains( Clear() Length ToUpper() ToLower() Trim() Split( Replace( Substring( IndexOf( ToString() ContainsKey( TryGetValue("),
  snip: [
    S("cw", "Console.WriteLine()", "Console.WriteLine(${0});"),
    S("main", "static void Main", "static void Main(string[] args)\n{\n\t${0}\n}"),
    S("for", "for", "for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++)\n{\n\t${0}\n}"),
    S("foreach", "foreach", "foreach (var ${1:elemento} in ${2:lista})\n{\n\t${0}\n}"),
    S("if", "if", "if (${1:condicion})\n{\n\t${0}\n}"),
    S("class", "Clase", "public class ${1:Nombre}\n{\n\t${0}\n}"),
    S("prop", "Propiedad", "public ${1:int} ${2:Nombre} { get; set; }$0"),
    S("try", "try / catch", "try\n{\n\t${1}\n}\ncatch (${2:Exception} e)\n{\n\t${0}\n}"),
  ],
};

const PHP = {
  kw: lista("abstract and array as break callable case catch class clone const continue declare default do echo else elseif empty enddeclare endfor endforeach endif endswitch endwhile extends final finally fn for foreach function global goto if implements include include_once instanceof insteadof interface isset list match namespace new or print private protected public require require_once return static switch throw trait try unset use var while yield true false null"),
  fn: lista("echo strlen( count( isset( empty( array_push( array_pop( array_merge( array_keys( array_values( in_array( explode( implode( str_replace( strtolower( strtoupper( trim( substr( strpos( json_encode( json_decode( htmlspecialchars( password_hash( password_verify( mysqli_connect( mysqli_query( mysqli_fetch_assoc( mysqli_close( header( session_start() date( time() var_dump( print_r( intval( round( rand( file_get_contents( die( $_POST $_GET $_SESSION $_SERVER PDO"),
  metodos: lista("prepare( execute( fetch( fetchAll( query( lastInsertId() bind_param( get_result() fetch_assoc() num_rows close()"),
  snip: [
    S("php", "<?php … ?>", "<?php\n${0}\n?>"),
    S("echo", "echo", "echo ${1:\"\"};$0"),
    S("function", "Función", "function ${1:nombre}(${2}) {\n\t${0}\n}"),
    S("foreach", "foreach", "foreach (${1:\\$lista} as ${2:\\$elemento}) {\n\t${0}\n}"),
    S("for", "for", "for (${1:\\$i} = 0; ${1:\\$i} < ${2:10}; ${1:\\$i}++) {\n\t${0}\n}"),
    S("if", "if", "if (${1:condicion}) {\n\t${0}\n}"),
    S("class", "Clase", "class ${1:Nombre} {\n\tpublic function __construct(${2}) {\n\t\t${0}\n\t}\n}"),
    S("pdo", "Conectar a MySQL con PDO", "\\$conexion = new PDO(\"mysql:host=localhost;dbname=${1:mi_base};charset=utf8mb4\", \"root\", \"\");\n\\$conexion->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);$0"),
    S("mysqli", "Conectar con mysqli", "\\$conexion = mysqli_connect(\"localhost\", \"root\", \"\", \"${1:mi_base}\");\nif (!\\$conexion) {\n\tdie(\"Error: \" . mysqli_connect_error());\n}$0"),
  ],
};

const SQL = {
  kw: lista("SELECT FROM WHERE INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE DATABASE DROP ALTER ADD COLUMN PRIMARY KEY FOREIGN REFERENCES NOT NULL DEFAULT UNIQUE AUTO_INCREMENT AND OR IN LIKE BETWEEN IS AS ORDER BY GROUP HAVING LIMIT OFFSET JOIN INNER LEFT RIGHT ON DISTINCT UNION ALL EXISTS CASE WHEN THEN ELSE END IF USE SHOW TABLES DESCRIBE INDEX VIEW CONSTRAINT CASCADE ASC DESC TRUNCATE COMMIT ROLLBACK"),
  fn: lista("COUNT( SUM( AVG( MIN( MAX( NOW() CURDATE() CONCAT( UPPER( LOWER( LENGTH( ROUND( COALESCE( IFNULL( DATE_FORMAT( YEAR( MONTH( DAY( SUBSTRING( TRIM( REPLACE("),
  tipos: lista("INT INTEGER BIGINT TINYINT SMALLINT DECIMAL FLOAT DOUBLE VARCHAR CHAR TEXT LONGTEXT DATE DATETIME TIMESTAMP TIME BOOLEAN ENUM BLOB JSON"),
  snip: [
    S("sel", "SELECT", "SELECT ${1:*} FROM ${2:tabla}${3: WHERE ${4:condicion}};$0"),
    S("ins", "INSERT", "INSERT INTO ${1:tabla} (${2:columnas}) VALUES (${3:valores});$0"),
    S("upd", "UPDATE", "UPDATE ${1:tabla} SET ${2:columna} = ${3:valor} WHERE ${4:id} = ${5:1};$0"),
    S("del", "DELETE", "DELETE FROM ${1:tabla} WHERE ${2:id} = ${3:1};$0"),
    S("ct", "CREATE TABLE", "CREATE TABLE ${1:tabla} (\n\tid INT AUTO_INCREMENT PRIMARY KEY,\n\t${2:nombre} VARCHAR(${3:100}) NOT NULL${0}\n);"),
    S("join", "INNER JOIN", "INNER JOIN ${1:tabla} ON ${2:a.id} = ${3:b.id}$0"),
    S("fk", "Llave foránea", "FOREIGN KEY (${1:columna}) REFERENCES ${2:tabla}(${3:id})$0"),
  ],
};

const OTROS = {
  go: { kw: lista("break case chan const continue default defer else fallthrough for func go goto if import interface map package range return select struct switch type var nil true false string int float64 bool error byte rune len append make new fmt"),
    miembros: { fmt: "Println( Printf( Sprintf( Print( Scan( Scanln( Errorf(", strings: "Split( Join( Contains( ToUpper( ToLower( TrimSpace( Replace(", strconv: "Itoa( Atoi( ParseFloat(" },
    snip: [S("main", "func main()", "package main\n\nimport \"fmt\"\n\nfunc main() {\n\t${0:fmt.Println(\"Hola\")}\n}"), S("func", "Función", "func ${1:nombre}(${2}) ${3}{\n\t${0}\n}"), S("for", "for", "for ${1:i} := 0; ${1:i} < ${2:n}; ${1:i}++ {\n\t${0}\n}"), S("if", "if", "if ${1:condicion} {\n\t${0}\n}"), S("iferr", "if err != nil", "if err != nil {\n\t${0:return err}\n}")] },
  rs: { kw: lista("as break const continue crate else enum extern false fn for if impl in let loop match mod move mut pub ref return self Self static struct super trait true type unsafe use where while async await dyn String Vec Option Some None Result Ok Err Box println! print! format! vec!"),
    snip: [S("main", "fn main()", "fn main() {\n\t${0}\n}"), S("fn", "Función", "fn ${1:nombre}(${2}) ${3:-> ${4:()} }{\n\t${0}\n}"), S("println", "println!", "println!(\"${1:{}}\", ${2});$0"), S("for", "for", "for ${1:i} in ${2:0..10} {\n\t${0}\n}"), S("match", "match", "match ${1:valor} {\n\t${2:_} => ${0},\n}")] },
  rb: { kw: lista("BEGIN END alias and begin break case class def defined? do else elsif end ensure false for if in module next nil not or redo rescue retry return self super then true undef unless until when while yield puts print gets require attr_accessor"),
    snip: [S("def", "Método", "def ${1:nombre}(${2})\n\t${0}\nend"), S("each", "each", "${1:lista}.each do |${2:x}|\n\t${0}\nend"), S("if", "if", "if ${1:condicion}\n\t${0}\nend"), S("class", "Clase", "class ${1:Nombre}\n\tdef initialize(${2})\n\t\t${0}\n\tend\nend")] },
  kt: { kw: lista("as break class continue do else false for fun if in interface is null object package return super this throw true try typealias val var when while data enum open override private public internal lateinit println readLine listOf mutableListOf mapOf String Int Double Boolean"),
    snip: [S("main", "fun main()", "fun main() {\n\t${0}\n}"), S("fun", "Función", "fun ${1:nombre}(${2}): ${3:Unit} {\n\t${0}\n}"), S("for", "for", "for (${1:i} in ${2:0 until 10}) {\n\t${0}\n}"), S("when", "when", "when (${1:valor}) {\n\t${2:1} -> ${0}\n\telse -> {}\n}")] },
  swift: { kw: lista("class deinit enum extension func import init let protocol struct subscript typealias var break case continue default do else fallthrough for guard if in repeat return switch where while as false is nil self super throw throws true try print String Int Double Bool Array"),
    snip: [S("func", "Función", "func ${1:nombre}(${2}) ${3:-> ${4:Void} }{\n\t${0}\n}"), S("for", "for", "for ${1:i} in ${2:0..<10} {\n\t${0}\n}"), S("if", "if", "if ${1:condicion} {\n\t${0}\n}")] },
  sh: { kw: lista("if then else elif fi for while do done case esac in function return echo exit export local read cd ls mkdir rm cp mv cat grep sed awk chmod pwd source test"),
    snip: [S("if", "if", "if [ ${1:condicion} ]; then\n\t${0}\nfi"), S("for", "for", "for ${1:x} in ${2:lista}; do\n\t${0}\ndone"), S("fn", "Función", "${1:nombre}() {\n\t${0}\n}"), S("shebang", "#!/bin/bash", "#!/usr/bin/env bash\n$0")] },
};

const DATOS = { py: PY, js: JS, html: HTML, css: CSS, java: JAVA, c: C, cs: CS, php: PHP, sql: SQL, ...OTROS };
const SENSIBLE = new Set(["py", "js", "java", "c", "cs", "php", "go", "rs", "rb", "kt", "swift", "sh"]); // distingue mayúsculas

// Documentación corta (en español) de lo que más se usa.
const DOC = {
  "py:print": "Muestra valores en la consola. `print(valor, sep=\" \", end=\"\\n\")`",
  "py:input": "Pide un texto a la persona. Devuelve siempre un str: usa int() o float() para números.",
  "py:len": "Cantidad de elementos de una lista, texto, diccionario…",
  "py:range": "Secuencia de números: range(fin), range(inicio, fin) o range(inicio, fin, paso). El fin no se incluye.",
  "py:int": "Convierte a número entero.", "py:float": "Convierte a número decimal.", "py:str": "Convierte a texto.",
  "py:open": "Abre un archivo. Modos: \"r\" leer, \"w\" escribir, \"a\" agregar. Mejor dentro de un `with`.",
  "py:enumerate": "Recorre una lista dando (posición, valor).", "py:zip": "Junta varias listas elemento a elemento.",
  "py:sorted": "Devuelve una lista ordenada (no cambia la original).", "py:isinstance": "¿El valor es de ese tipo?",
  "js:console": "Mensajes en la consola: console.log(), console.error()…", "js:fetch": "Pide datos a una URL. Devuelve una promesa.",
  "js:document": "La página: buscar elementos, crearlos, escuchar eventos.",
  "java:System": "System.out.println() escribe en la consola.", "java:Scanner": "Lee lo que escribe la persona: new Scanner(System.in).",
};

// ------------------------------------------------------------------------- proyecto y documento ----
const IDENT = /[A-Za-z_$][\w$]{2,}/g;
const cache = new Map(); // ruta -> { texto, palabras }

function palabrasDe(texto) {
  const s = new Set();
  const limpio = texto.length > 400_000 ? texto.slice(0, 400_000) : texto;
  for (const m of limpio.matchAll(IDENT)) s.add(m[0]);
  return s;
}
function palabrasCacheadas(ruta, texto) {
  const c = cache.get(ruta);
  if (c && c.texto === texto) return c.palabras;
  const palabras = palabrasDe(texto);
  cache.set(ruta, { texto, palabras });
  return palabras;
}

/** Símbolos definidos en un archivo (funciones, clases, variables) para mostrarlos con su ícono. */
function simbolos(fam, texto) {
  const r = new Map();
  const poner = (n, tipo) => { if (n && !r.has(n)) r.set(n, tipo); };
  const T = texto.length > 400_000 ? texto.slice(0, 400_000) : texto;
  const reglas = {
    py: [[/^\s*(?:async\s+)?def\s+(\w+)/gm, "fn"], [/^\s*class\s+(\w+)/gm, "clase"], [/^\s*(\w+)\s*(?::[^=\n]+)?=(?!=)/gm, "var"], [/^\s*for\s+(\w+)(?:\s*,\s*(\w+))?\s+in\b/gm, "var"], [/\bimport\s+(\w+)/g, "mod"], [/\bas\s+(\w+)/g, "var"]],
    js: [[/\bfunction\s*\*?\s*(\w+)/g, "fn"], [/\bclass\s+(\w+)/g, "clase"], [/\b(?:const|let|var)\s+(\w+)/g, "var"], [/\b(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>/g, "fn"]],
    java: [[/\bclass\s+(\w+)/g, "clase"], [/\b(?:public|private|protected|static|\s)+[\w<>[\],\s]+\s+(\w+)\s*\([^)]*\)\s*\{/g, "fn"], [/\b(?:int|double|float|long|String|boolean|char|var|[A-Z]\w*(?:<[^>]*>)?)\s+(\w+)\s*[=;]/g, "var"]],
    c: [[/\b(?:int|void|float|double|char|bool|long|auto|string)\s+\*?(\w+)\s*\(/g, "fn"], [/\b(?:int|float|double|char|bool|long|auto|string)\s+\*?(\w+)\s*[=;[]/g, "var"], [/\bstruct\s+(\w+)/g, "clase"]],
    cs: [[/\bclass\s+(\w+)/g, "clase"], [/\b(?:void|int|string|bool|double|var|Task)\s+(\w+)\s*\(/g, "fn"]],
    php: [[/\bfunction\s+(\w+)/g, "fn"], [/\bclass\s+(\w+)/g, "clase"], [/(\$\w+)/g, "var"]],
    go: [[/\bfunc\s+(?:\([^)]*\)\s*)?(\w+)/g, "fn"], [/\b(\w+)\s*:=/g, "var"], [/\btype\s+(\w+)/g, "clase"]],
    rs: [[/\bfn\s+(\w+)/g, "fn"], [/\blet\s+(?:mut\s+)?(\w+)/g, "var"], [/\b(?:struct|enum)\s+(\w+)/g, "clase"]],
    rb: [[/\bdef\s+(?:self\.)?(\w+[?!]?)/g, "fn"], [/\bclass\s+(\w+)/g, "clase"]],
    kt: [[/\bfun\s+(\w+)/g, "fn"], [/\b(?:val|var)\s+(\w+)/g, "var"], [/\bclass\s+(\w+)/g, "clase"]],
    swift: [[/\bfunc\s+(\w+)/g, "fn"], [/\b(?:let|var)\s+(\w+)/g, "var"], [/\b(?:class|struct)\s+(\w+)/g, "clase"]],
    sh: [[/^\s*(\w+)\s*\(\)\s*\{/gm, "fn"], [/^\s*(?:export\s+)?(\w+)=/gm, "var"]],
  }[fam] ?? [];
  for (const [re, tipo] of reglas) for (const m of T.matchAll(re)) { poner(m[1], tipo); if (m[2]) poner(m[2], tipo); }
  return r;
}

/** Tablas y columnas de los CREATE TABLE del proyecto (en .sql o dentro de strings de Python/PHP/JS). */
export function esquemaSql(archivos) {
  const tablas = new Map();
  for (const [ruta, texto] of archivos) {
    if (typeof texto !== "string" || texto.length > 2_000_000 || !/create\s+table/i.test(texto)) continue;
    const re = /create\s+table\s+(?:if\s+not\s+exists\s+)?[`"[]?(\w+)[`"\]]?\s*\(/gi;
    for (let m = re.exec(texto); m; m = re.exec(texto)) {
      let nivel = 1, i = re.lastIndex;
      for (; i < texto.length && nivel; i += 1) { if (texto[i] === "(") nivel += 1; else if (texto[i] === ")") nivel -= 1; }
      const cuerpo = texto.slice(re.lastIndex, i - 1);
      const cols = tablas.get(m[1]) ?? new Set();
      let prof = 0, trozo = "";
      const partes = [];
      for (const ch of cuerpo) { if (ch === "(") prof += 1; if (ch === ")") prof -= 1; if (ch === "," && !prof) { partes.push(trozo); trozo = ""; } else trozo += ch; }
      partes.push(trozo);
      for (const p of partes) {
        const c = /^\s*[`"[]?(\w+)[`"\]]?/.exec(p)?.[1];
        if (c && !/^(primary|foreign|key|unique|constraint|index|check|fulltext)$/i.test(c)) cols.add(c);
      }
      tablas.set(m[1], cols);
      void ruta;
    }
  }
  return tablas;
}

// -------------------------------------------------------------------------------------- Emmet ----
/** Expande una abreviatura Emmet sencilla (div.caja#id>ul>li*3{texto}+p) a un fragmento con $1, $2… o null. */
export function expandirEmmet(abbr) {
  if (!abbr || abbr.length > 120 || /[^\w.#>+*{}$:\- \[\]="'áéíóúñÁÉÍÓÚÑ!?,]/.test(abbr)) return null;
  let n = 0;
  const marcador = () => `\${${++n}}`;
  // Analiza en un árbol de hermanos e hijos.
  let i = 0;
  const leerElemento = () => {
    const m = /^([a-zA-Z][\w:-]*)?((?:[.#][\w$-]+)*)((?:\[[^\]]*\])?)(?:\{([^}]*)\})?(?:\*(\d{1,2}))?(?:\{([^}]*)\})?/.exec(abbr.slice(i));
    if (!m || !m[0]) return null;
    i += m[0].length;
    const tag = (m[1] || "div").toLowerCase();
    if (m[1] && !HTML_TAGS.includes(tag) && !/^[a-z]+-[a-z-]+$/.test(tag)) return { malo: true };
    const ids = [...m[2].matchAll(/#([\w$-]+)/g)].map((x) => x[1]);
    const clases = [...m[2].matchAll(/\.([\w$-]+)/g)].map((x) => x[1]);
    const attrs = m[3] ? m[3].slice(1, -1).trim() : "";
    return { tag, ids, clases, attrs, texto: m[4] ?? m[6], veces: Math.min(Number(m[5] || 1), 50), hijos: [] };
  };
  const leerGrupo = () => {
    const hermanos = [];
    for (;;) {
      const e = leerElemento();
      if (!e || e.malo) return null;
      hermanos.push(e);
      if (abbr[i] === ">") { i += 1; const h = leerGrupo(); if (!h) return null; e.hijos = h; return hermanos; }
      if (abbr[i] === "+") { i += 1; continue; }
      return hermanos;
    }
  };
  const arbol = leerGrupo();
  if (!arbol || i !== abbr.length) return null;
  const simple = arbol.length === 1 && !arbol[0].hijos.length && arbol[0].veces === 1 && !arbol[0].ids.length && !arbol[0].clases.length && !arbol[0].attrs && arbol[0].texto === undefined;
  if (simple && !HTML_TAGS.includes(abbr)) return null;
  const ATR = { a: ' href="$H"', img: ' src="$H" alt="$H"', input: ' type="text"', link: ' rel="stylesheet" href="$H"', script: ' src="$H"', form: ' action="$H"', label: ' for="$H"', iframe: ' src="$H"', source: ' src="$H"', video: ' src="$H"', audio: ' src="$H"' };
  const pintar = (nodos, sangria) => nodos.map((e) => {
    let s = "";
    for (let k = 1; k <= e.veces; k += 1) {
      const sust = (t) => t.replace(/\$+/g, (d) => String(k).padStart(d.length, "0"));
      let a = "";
      if (e.ids.length) a += ` id="${sust(e.ids.at(-1))}"`;
      if (e.clases.length) a += ` class="${sust(e.clases.join(" "))}"`;
      if (e.attrs) a += " " + e.attrs.split(/\s+/).filter(Boolean).map((x) => { const [k, ...v] = x.split("="); const val = v.join("=").replace(/^["']|["']$/g, ""); return `${k}="${val}"`; }).join(" ");
      else if (ATR[e.tag]) a += ATR[e.tag].replace(/\$H/g, () => marcador());
      const abre = `<${e.tag}${a}>`;
      if (HTML_VACIAS.has(e.tag)) { s += `${sangria}${abre}\n`; continue; }
      if (e.hijos.length) s += `${sangria}${abre}\n${pintar(e.hijos, sangria + "\t")}${sangria}</${e.tag}>\n`;
      else s += `${sangria}${abre}${e.texto !== undefined ? sust(e.texto) : marcador()}</${e.tag}>\n`;
    }
    return s;
  }).join("");
  return pintar(arbol, "").replace(/\n$/, "") + (n ? "" : "$0");
}

// ------------------------------------------------------------------------------- sugerencias ----
/**
 * Sugerencias para la posición del cursor.
 * @param {{ ext:string, linea:string (texto de la línea hasta el cursor), documento:string, ruta?:string,
 *           archivos?: Iterable<[string,string]>, monaco?: boolean }} o
 *   monaco=true: no repite lo que Monaco ya da (IntelliSense de JS/TS/CSS y etiquetas de HTML).
 * @returns {{ prefijo:number, items: {etiqueta, tipo, insertar, detalle?, doc?, snippet?:boolean, orden?:string}[] }}
 */
export function sugerir({ ext, linea, documento = "", ruta = "", archivos = [], monaco = false }) {
  const fam = familiaDe(ext);
  const vacio = { prefijo: 0, items: [] };
  const D = DATOS[fam];
  if (!D) return vacio;
  if (enComentarioOTexto(fam, linea)) return vacio;
  const items = [];
  const vistos = new Set();
  const add = (it) => { const k = `${it.etiqueta}\u0000${it.tipo === "snip" ? "s" : ""}`; if (vistos.has(k)) return; vistos.add(k); items.push(it); };
  const comoFuncion = (n, tipo) => {
    if (n.endsWith("()")) return { etiqueta: n.slice(0, -2), tipo, insertar: `${n}$0`, snippet: true, detalle: "()" };
    if (n.endsWith("(")) return { etiqueta: n.slice(0, -1), tipo, insertar: `${n}$0)`, snippet: true, detalle: "(…)" };
    return { etiqueta: n, tipo: tipo === "metodo" ? "prop" : tipo, insertar: n };
  };

  // --- HTML: Emmet y fragmentos (Monaco ya sugiere etiquetas tras "<").
  if (fam === "html") {
    if (/<[^>]*$/.test(linea)) return vacio;                         // dentro de una etiqueta: lo hace Monaco
    const mm = /(^|[\s>])([!a-zA-Z.#][\w.#>+*{}$:\-\[\]="'!]*)$/.exec(linea);
    const abbr = mm?.[2] ?? "";
    if (!abbr) return vacio;
    // Una palabra suelta (p, a, div…) solo se ofrece como etiqueta al empezar la línea o justo después de otra
    // etiqueta, para no estorbar cuando escribes texto normal.
    const alInicio = /^\s*$/.test(linea.slice(0, mm.index + mm[1].length)) || mm[1] === ">";
    for (const s of HTML.snip) add({ etiqueta: s.atajo, tipo: "snip", insertar: s.cuerpo, snippet: true, detalle: s.desc, doc: vistaFragmento(s.cuerpo) });
    // Mientras escribes «ul>li*» (a medias) se sigue mostrando lo que ya se puede expandir.
    const em = /^[a-z][\w-]*$/i.test(abbr) && !alInicio ? null : expandirEmmet(abbr) ?? expandirEmmet(abbr.replace(/[>+*.#{[]+$/, "")) ?? expandirEmmet(abbr.replace(/[>+][^>+]*$/, ""));
    if (em) add({ etiqueta: abbr, tipo: "emmet", insertar: em, snippet: true, detalle: "Emmet", doc: vistaFragmento(em), orden: "0" });
    if (!monaco && alInicio) for (const t of HTML_TAGS) if (t.startsWith(abbr.toLowerCase()) && t !== abbr) add({ etiqueta: t, tipo: "emmet", insertar: expandirEmmet(t), snippet: true, detalle: `<${t}>` });
    return { prefijo: abbr.length, items: items.filter((x) => coincide(x.etiqueta, abbr, false, true)) };
  }
  if (fam === "css" && monaco) {
    const p = /([\w-]*)$/.exec(linea)[1];
    for (const s of CSS.snip) add({ etiqueta: s.atajo, tipo: "snip", insertar: s.cuerpo, snippet: true, detalle: s.desc, doc: vistaFragmento(s.cuerpo) });
    return { prefijo: p.length, items: items.filter((x) => coincide(x.etiqueta, p, false, x.tipo === "snip")) };
  }

  const sens = SENSIBLE.has(fam);
  // --- import de Python
  if (fam === "py") {
    const imp = /^\s*(?:import|from)\s+([\w.]*)$/.exec(linea);
    if (imp) {
      const p = imp[1];
      for (const m of PY.modulos) add({ etiqueta: m, tipo: "mod", insertar: m });
      for (const [r] of archivos) if (r.endsWith(".py") && r !== ruta) { const m = r.replace(/\.py$/, "").replace(/\//g, "."); add({ etiqueta: m, tipo: "mod", insertar: m, detalle: "de tu proyecto" }); }
      const ult = p.lastIndexOf(".");
      return { prefijo: p.length, items: items.filter((x) => x.etiqueta.startsWith(p.slice(0, ult + 1)) && coincide(x.etiqueta, p, true)) };
    }
    const desde = /^\s*from\s+([\w.]+)\s+import\s+(?:.*,\s*)?(\w*)$/.exec(linea);
    if (desde) {
      const miembros = PY.miembros[desde[1]];
      if (miembros) for (const n of lista(miembros)) add({ etiqueta: n.replace(/\(\)?$/, ""), tipo: "fn", insertar: n.replace(/\(\)?$/, "") });
      return { prefijo: desde[2].length, items: items.filter((x) => coincide(x.etiqueta, desde[2], true)) };
    }
  }

  // --- después de un punto: objeto.miembro
  const punto = /([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\.([\w$]*)$/.exec(linea);
  if (punto && monaco && fam === "js") return vacio;   // después del punto en JS/TS manda el IntelliSense de Monaco
  if (punto) {
    let [, objeto, p] = punto;
    if (fam === "py") objeto = aliasPython(documento)[objeto] ?? objeto;
    const M = D.miembros ?? {};
    const conocidos = M[objeto] ?? (objeto === "self" || objeto === "this" ? null : M[objeto.split(".").pop()]);
    if (conocidos) for (const n of lista(conocidos)) add({ ...comoFuncion(n, "metodo"), orden: "0" });
    else {
      if (objeto === "self" || objeto === "this") {
        for (const m of documento.matchAll(new RegExp(`\\b${objeto}\\.(\\w+)`, "g"))) add({ etiqueta: m[1], tipo: "prop", insertar: m[1], orden: "0" });
        for (const [n, t] of simbolos(fam, documento)) if (t === "fn") add({ etiqueta: n, tipo: "metodo", insertar: `${n}($0)`, snippet: true, orden: "1" });
      }
      if (fam === "sql") for (const c of esquemaSql([[ruta, documento], ...archivos]).get(objeto) ?? []) add({ etiqueta: c, tipo: "columna", insertar: c, orden: "0" });
      for (const m of documento.matchAll(/\.([A-Za-z_]\w+)/g)) if (m[1] !== p) add({ etiqueta: m[1], tipo: "prop", insertar: m[1], orden: "2" });
      for (const n of D.metodos ?? []) add({ ...comoFuncion(n, "metodo"), orden: "3" });
    }
    return { prefijo: p.length, items: ordenar(items.filter((x) => coincide(x.etiqueta, p, sens)), p) };
  }

  // --- palabra normal
  const p = (fam === "php" ? /(\$?[\w]*)$/ : /([A-Za-z_$][\w$]*|)$/).exec(linea)[1];
  if (!p) return vacio;
  if (/^\d/.test(p)) return vacio;
  if (!(monaco && fam === "js")) {
    for (const [n, t] of simbolos(fam, documento)) if (n !== p) add({ etiqueta: n, tipo: t, insertar: t === "fn" || (t === "clase" && fam === "py") ? `${n}($0)` : n, snippet: t === "fn" || (t === "clase" && fam === "py"), orden: "0" });
  }
  for (const s of D.snip ?? []) add({ etiqueta: s.atajo, tipo: "snip", insertar: s.cuerpo, snippet: true, detalle: s.desc, doc: vistaFragmento(s.cuerpo), orden: "1" });
  if (!(monaco && fam === "js")) {
    for (const k of D.kw ?? []) add({ etiqueta: k, tipo: "kw", insertar: k, orden: "2" });
    for (const n of D.fn ?? []) { const it = comoFuncion(n, "fn"); add({ ...it, tipo: /^[A-Z]/.test(it.etiqueta) && !n.endsWith("(") ? "clase" : "fn", doc: DOC[`${fam}:${it.etiqueta}`], orden: "1" }); }
    for (const t of D.tipos ?? []) add({ etiqueta: t, tipo: "tipo", insertar: t, orden: "2" });
    if (D.miembros) for (const k of Object.keys(D.miembros)) if (!k.includes(".")) add({ etiqueta: k, tipo: "mod", insertar: k, orden: "2" });
    if (fam === "sql") for (const [t, cols] of esquemaSql([[ruta, documento], ...archivos])) { add({ etiqueta: t, tipo: "tabla", insertar: t, detalle: "tabla", orden: "0" }); for (const c of cols) add({ etiqueta: c, tipo: "columna", insertar: c, detalle: `columna de ${t}`, orden: "1" }); }
    // Palabras del documento y de los demás archivos del mismo lenguaje (como VS Code).
    const deDoc = palabrasDe(documento);
    deDoc.delete(p);
    for (const w of deDoc) add({ etiqueta: w, tipo: "palabra", insertar: w, orden: "3" });
    let n = 0;
    for (const [r, texto] of archivos) {
      if (r === ruta || familiaDe(r.split(".").pop()) !== fam || typeof texto !== "string" || texto.length > 1_000_000) continue;
      if ((n += 1) > 150) break;
      for (const w of palabrasCacheadas(r, texto)) if (w !== p) add({ etiqueta: w, tipo: "palabra", insertar: w, detalle: r, orden: "4" });
    }
  }
  return { prefijo: p.length, items: ordenar(items.filter((x) => coincide(x.etiqueta, p, fam !== "sql" && sens, x.tipo === "snip")), p) };
}

function enComentarioOTexto(fam, linea) {
  const sinTextos = linea.replace(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`/g, "\"\"");
  if (/["'`][^"'`]*$/.test(sinTextos) && fam !== "html") return true;        // dentro de un texto sin cerrar
  const c = { py: "#", rb: "#", sh: "#", sql: "--" }[fam] ?? (fam === "css" ? "/*" : "//");
  return sinTextos.includes(c);
}

function aliasPython(doc) {
  const r = {};
  for (const m of doc.matchAll(/^\s*import\s+([\w.]+)\s+as\s+(\w+)/gm)) r[m[2]] = m[1];
  for (const m of doc.matchAll(/^\s*from\s+([\w.]+)\s+import\s+(\w+)\s+as\s+(\w+)/gm)) r[m[3]] = `${m[1]}.${m[2]}`;
  for (const m of doc.matchAll(/^\s*from\s+([\w.]+)\s+import\s+([\w, ]+)$/gm)) for (const n of m[2].split(",").map((x) => x.trim())) if (n && !r[n]) r[n] = `${m[1]}.${n}`;
  return r;
}

/** ¿`etiqueta` sirve para lo que se escribió? Prefijo, o letras en orden (como VS Code: "pt" -> "print"). */
export function coincide(etiqueta, p, sensible = true, igual = false) {
  if (!p) return true;
  const a = sensible ? etiqueta : etiqueta.toLowerCase();
  const b = sensible ? p : p.toLowerCase();
  if (a === b) return igual;   // lo que ya escribiste no se sugiere (salvo fragmentos: «def» + Enter lo expande)
  if (a.toLowerCase().startsWith(b.toLowerCase())) return true;
  if (a[0].toLowerCase() !== b[0].toLowerCase()) return false;
  let i = 0;
  for (const ch of a.toLowerCase()) if (ch === b[i]?.toLowerCase()) i += 1;
  return i === b.length;
}

function ordenar(items, p) {
  const pl = p.toLowerCase();
  const peso = (x) => (x.etiqueta.startsWith(p) ? 0 : x.etiqueta.toLowerCase().startsWith(pl) ? 1 : 2);
  return items.map((x, i) => ({ x, i })).sort((u, v) => peso(u.x) - peso(v.x) || (u.x.orden ?? "5").localeCompare(v.x.orden ?? "5") || u.x.etiqueta.length - v.x.etiqueta.length || u.i - v.i).map((o) => o.x);
}

/** Texto plano de un fragmento para la vista previa: ${1:nombre} -> nombre, \t -> 4 espacios. */
export function vistaFragmento(cuerpo) {
  return fragmentoAPlano(cuerpo, "    ").texto;
}

/**
 * Convierte un fragmento a texto plano para el editor simple.
 * Devuelve { texto, desde, hasta } con la selección del primer marcador (o el cursor en $0).
 */
export function fragmentoAPlano(cuerpo, unidad = "  ", sangria = "") {
  let texto = "";
  const marcas = {};
  let i = 0;
  const valores = {};
  while (i < cuerpo.length) {
    const ch = cuerpo[i];
    if (ch === "\\" && i + 1 < cuerpo.length) { texto += cuerpo[i + 1]; i += 2; continue; }
    if (ch === "$") {
      const m = /^\$(?:(\d+)|\{(\d+)(?::((?:[^{}\\]|\\.|\{[^{}]*\})*))?\})/.exec(cuerpo.slice(i));
      if (m) {
        const num = m[1] ?? m[2];
        let def = m[3] !== undefined ? fragmentoAPlano(m[3], unidad).texto : valores[num] ?? "";
        if (m[3] === undefined && valores[num] !== undefined) def = valores[num];
        if (marcas[num] === undefined) { marcas[num] = [texto.length, texto.length + def.length]; valores[num] = def; }
        texto += def;
        i += m[0].length;
        continue;
      }
    }
    if (ch === "\t") texto += unidad;
    else if (ch === "\n") texto += `\n${sangria}`;
    else texto += ch;
    i += 1;
  }
  const primero = Object.keys(marcas).filter((k) => k !== "0").sort((a, b) => a - b)[0];
  const [desde, hasta] = marcas[primero ?? "0"] ?? [texto.length, texto.length];
  return { texto, desde, hasta };
}

// ----------------------------------------------------------------------------------- Monaco ----
const KIND = { kw: "Keyword", fn: "Function", metodo: "Method", var: "Variable", clase: "Class", mod: "Module", snip: "Snippet", prop: "Property",
  palabra: "Text", tabla: "Struct", columna: "Field", tipo: "TypeParameter", emmet: "Snippet" };

let registrado = false;
/**
 * Registra los proveedores de sugerencias en Monaco.
 * @param {object} monaco
 * @param {() => Record<string,string>} obtenerArchivos  archivos del proyecto abierto (ruta -> texto)
 */
export function registrarEnMonaco(monaco, obtenerArchivos) {
  if (registrado) return;
  registrado = true;
  const L = monaco.languages;
  const K = L.CompletionItemKind;
  const ids = ["python", "java", "c", "cpp", "csharp", "php", "sql", "go", "rust", "ruby", "kotlin", "swift", "shell", "javascript", "typescript", "html", "css", "scss", "less"];
  for (const id of ids) {
    const fam = FAMILIA_MONACO[id];
    L.registerCompletionItemProvider(id, {
      triggerCharacters: fam === "html" ? [".", "#", ">", "*", "+", "!", ..."0123456789"] : fam === "js" || fam === "css" ? [] : ["."],
      provideCompletionItems(modelo, pos) {
        const linea = modelo.getValueInRange({ startLineNumber: pos.lineNumber, startColumn: 1, endLineNumber: pos.lineNumber, endColumn: pos.column });
        const ruta = decodeURIComponent(modelo.uri.path.replace(/^\/workspace\//, ""));
        const ext = fam === "html" ? "html" : fam === "css" ? "css" : ruta.includes(".") ? ruta.split(".").pop() : { python: "py", java: "java", shell: "sh" }[id] ?? fam;
        let archivos = [];
        try { archivos = Object.entries(obtenerArchivos() ?? {}); } catch { /* sin proyecto */ }
        const doc = modelo.getValueLength() > 600_000 ? "" : modelo.getValue();
        const { prefijo, items } = sugerir({ ext: familiaDe(ext) ? ext : fam, linea, documento: doc, ruta, archivos, monaco: true });
        const rango = { startLineNumber: pos.lineNumber, endLineNumber: pos.lineNumber, startColumn: pos.column - prefijo, endColumn: pos.column };
        const texto = linea.slice(linea.length - prefijo);
        return {
          incomplete: true,   // se recalcula con cada letra (Emmet a medias, y no sugerir lo que ya escribiste)
          suggestions: items.slice(0, 400).map((it, i) => ({
            label: it.detalle && it.tipo !== "palabra" ? { label: it.etiqueta, description: it.detalle } : it.etiqueta,
            kind: K[KIND[it.tipo]] ?? K.Text,
            insertText: it.insertar,
            insertTextRules: it.snippet ? L.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
            documentation: it.doc ? (it.tipo === "snip" || it.tipo === "emmet" ? { value: "```\n" + it.doc + "\n```" } : it.doc) : undefined,
            detail: it.tipo === "palabra" && it.detalle ? it.detalle : undefined,
            range: rango,
            filterText: it.tipo === "emmet" ? texto : undefined,
            sortText: `${it.orden ?? "5"}${String(i).padStart(4, "0")}`,
            preselect: i === 0 && it.tipo === "emmet",
          })),
        };
      },
    });
  }
}

/** Opciones del editor Monaco para que sugiera mientras escribes y Enter acepte (como VS Code). */
export const OPCIONES_MONACO = {
  quickSuggestions: { other: "on", comments: "off", strings: "on" },
  quickSuggestionsDelay: 10,
  suggestOnTriggerCharacters: true,
  acceptSuggestionOnEnter: "on",
  acceptSuggestionOnCommitCharacter: true,
  tabCompletion: "on",
  snippetSuggestions: "inline",
  wordBasedSuggestions: "matchingDocuments",
  suggestSelection: "first",
  parameterHints: { enabled: true },
  inlineSuggest: { enabled: true },
  suggest: { preview: true, showWords: true, showSnippets: true, localityBonus: true, filterGraceful: true, snippetsPreventQuickSuggestions: false, insertMode: "replace", showStatusBar: false },
};
