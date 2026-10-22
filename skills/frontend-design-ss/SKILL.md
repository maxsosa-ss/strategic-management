---
name: frontend-design-ss
description: Guía para lograr un diseño visual distintivo e intencional al construir una interfaz nueva o rediseñar una existente, usando la paleta, la tipografía y los íconos de la marca de la empresa. Ayuda con el layout, la jerarquía y a tomar decisiones que no se lean como valores predeterminados de plantilla.
license: Complete terms in LICENSE.txt
---

# Frontend Design

Encará esto como el líder de diseño de un estudio conocido por darle a cada cliente una identidad visual propia, que no se confunde con la de nadie más. Este cliente ya rechazó propuestas que sonaban clichés o armadas con plantilla, y paga por un punto de vista distintivo: tomá decisiones deliberadas y con opinión sobre el layout, la jerarquía y el movimiento, específicas de este brief. La paleta, las tipografías y los íconos los fija la marca (ver abajo), así que el riesgo estético va en cómo los componés, no en reemplazarlos.

## Marca: paleta, tipografía e íconos

El manual de marca define lo siguiente. Usalo tal cual: no sustituyas, no tiñas ni inventes colores de marca nuevos.

Paleta principal (los tres primeros son los colores principales, el resto son alternos):

| HEX | Uso |
|---|---|
| #278976 | Títulos, encabezados de visualizaciones, indicadores principales |
| #42E2C6 | Encabezados, subtítulos, indicadores principales |
| #ACF9EA | Indicadores secundarios, líneas de tendencia, valores de referencia |
| #C774BB | Indicadores secundarios, líneas de tendencia, valores de referencia |
| #FFA24D | Indicadores secundarios, líneas de tendencia, valores de referencia |
| #D9E67E | Indicadores secundarios, líneas de tendencia, valores de referencia |

Paleta adicional:

| HEX | Uso |
|---|---|
| #F1F3F3 | Fondo de página |
| #F9FAFA | Superficie que despega una visualización del fondo |
| #434343 | Líneas de tendencia, variaciones, texto de cuerpo |
| #67C978 | Estado: óptimo |
| #FCC358 | Estado: precaución |
| #F25757 | Estado: crítico |

Reglas de uso:
- Quedate con los tres colores principales. Sumá los alternos solo cuando una visualización tenga tantas métricas que los principales no alcancen.
- #42E2C6 y #ACF9EA no tienen contraste suficiente contra #F1F3F3 ni #F9FAFA para llevar texto. Usalos solo como rellenos, barras, líneas e indicadores. El texto va en #278976 (títulos grandes) o #434343.
- Los colores de estado significan estado. No uses verde, ámbar ni rojo como decoración ni para categorías.
- Tipografía: Roboto para títulos, Inter para párrafos. La personalidad sale del peso, el tamaño, el espaciado y la escala tipográfica, no de otras tipografías.
- Íconos: Boxicons (https://boxicons.com), un solo estilo en todo el diseño.

## Fundamentá tus diseños en el tema

Si el brief no identifica cuál es el producto o el tema, identificalo vos antes de diseñar y confirmalo con el cliente. Podés proponer un tema concreto, la audiencia del diseño y su tarea principal. Si tenés en memoria información sobre las preferencias del cliente o el contexto de lo que está construyendo, usala como pista. La industria, el tema, los materiales y el vocabulario del tema son de donde salen las decisiones distintivas de layout y contenido: el diseño de un juguete para chicas de 8 a 11 años va a ser estéticamente muy distinto de un dashboard para analistas financieros. Construí con el contenido y el tema reales del brief en todo momento.

## Principios de diseño

En los diseños web, el hero es lo primero que ven los usuarios. Abrí con lo más característico del mundo del tema, en la forma más apropiada: un titular, una imagen, una animación, una demo en vivo, un momento interactivo u otros tratamientos. Elegí con criterio: un número grande con una etiqueta chica, estadísticas de apoyo y un acento en degradé es el tratamiento por defecto, así que usalo solo si realmente es la mejor opción.

La tipografía lleva la personalidad de la página. La marca fija dos familias: Roboto para títulos e Inter para párrafos. Ya son claramente distintas, así que usalas en esos roles y no agregues una tercera.

Definí una escala tipográfica clara siguiendo la guía de The Elements of Typographic Style, con pesos, anchos y espaciados intencionales. Cuando el texto funcione como titular o elemento visual, usá el tratamiento tipográfico como parte activa del diseño y no como un vehículo neutro del contenido.

Por defecto, usá líneas de menos de 80 caracteres.

Evitá estos tratamientos tipográficos por defecto, que son las señales más comunes de una página generada:
- Resaltar una sola palabra o frase de un titular, como poner una palabra en itálica, negrita o de otro color.
- Usar todo en mayúsculas para las etiquetas.
- Agregar etiquetas tipográficas innecesarias sobre el contenido.

La estructura visual es información. Los recursos estructurales como contornos, bordes, numeración, antetítulos, divisores y etiquetas codifican información útil sobre el contenido en vez de decorar. Muchos diseños genéricos usan marcadores numerados (01 / 02 / 03), pero eso solo corresponde si el contenido realmente es una secuencia, como un proceso por pasos o una línea de tiempo. Antes de agregar marcadores numerados, verificá que el contenido sea de verdad una secuencia.

Usá el movimiento que no responde a una acción del usuario con moderación y con intención, solo para llamar la atención. Un único momento orquestado, una secuencia de carga o una revelación, funciona mejor que efectos dispersos: las entradas con fundido y deslizamiento en cada sección y las transiciones al pasar el cursor en cada tarjeta son el recurso genérico por defecto y se leen como hechas por IA. El movimiento que responde a una acción de la persona (abrir, expandir, confirmar) es bienvenido cuando muestra qué cambió.

Considerá con cuidado el contenido escrito. A menudo el brief no incluye contenido real y te toca a vos inventar el texto y el contenido de relleno. El texto puede hacer que un diseño se sienta tan de plantilla como el diseño mismo. Mirá la sección de abajo sobre escritura para más guía.

## Proceso: planificar, revisar contra el brief, construir, criticar

Como referencia, el diseño generado por IA hoy se agrupa en torno a ciertos rasgos. La paleta la da la marca, así que los rasgos ligados al color (un fondo crema cálido con acento terracota, o casi negro con un único acento ácido) no aplican acá. Estos sí:
1. un layout de diario, con filetes finos, cero border-radius y columnas densas tipo periódico;
2. el kit de tarjetas SaaS: el contenido cortado en tarjetas redondeadas idénticas, un mismo border-radius en todo sin importar la jerarquía, la misma sombra gris suave (rgba(0,0,0,.1)) debajo de cada una y degradés como decoración;
3. adornos de plantilla que aparecen sin importar el tema: una etiqueta en MAYÚSCULAS con tracking amplio sobre cada encabezado; cadenas de metadatos unidas con puntos medios ('A · B · C'); etiquetas armadas como 'PALABRA — fragmento' con raya larga espaciada; un casi negro teñido (#0B0B0B, #111) en lugar del negro; una tipografía monoespaciada para las etiquetas de datos chicas; una '→' al final del texto de enlaces y botones.

Todos esos rasgos son legítimos para algunos briefs, pero son valores por defecto y no elecciones, y aparecen sin importar el tema. Cuando el brief define una dirección visual, seguila al pie de la letra: las palabras del brief siempre ganan, incluso si piden uno de estos looks. Cuando deja libre un eje, no gastes esa libertad en uno de estos valores por defecto. Como con un diseñador humano contratado, suele haber un equilibrio delicado entre hacer lo que uno domina y tomar cada proyecto como una oportunidad para experimentar y aprender.

Trabajá en dos pasadas. Primero, pensá un plan de diseño breve a partir del brief del cliente: armá un sistema compacto de tokens con color, tipografía, layout y principios.
- Color: tomá la paleta de la marca y asigná un rol a cada color (fondo, superficie, texto, indicador principal, indicador secundario, estado). No agregues colores fuera de ella.
- Tipografía: Roboto para títulos e Inter para párrafos, con los tamaños, pesos y espaciados de la escala.
- Layout: un concepto de layout, con descripciones en prosa de una oración y wireframes en ASCII para idear y comparar. Incluí guía de alineación: ¿el contenido va alineado a la izquierda, centrado o justificado?
- Principios: la guía de alto nivel sobre qué hace único a esta página.

Después, revisá ese plan contra el brief antes de construir: si alguna parte se lee como el valor genérico que producirías para cualquier página parecida (probá resolver un pedido similar para ver si llegás a algo parecido) y no como una elección hecha para este brief, revisala e indicá qué cambiaste y por qué. Recién cuando hayas confirmado la relativa singularidad de tu plan de diseño, empezá a escribir el código siguiendo el plan revisado.

Al escribir el código, cuidá la especificidad de tus selectores CSS. Es fácil generar clases CSS que se anulan entre sí (sobre todo con un selector por tipo como .section y uno por elemento como .cta). Pasa seguido con el padding y el margin entre secciones.

## Moderación y autocrítica

Gastá tu audacia en un solo lugar. Dejá que un elemento sea el memorable, mantené todo lo que lo rodea callado y disciplinado, y cortá toda decoración que no sirva al brief. Construí con un piso de calidad sin anunciarlo: responsive hasta mobile, foco de teclado visible, movimiento reducido respetado, accesible visualmente (verificá el contraste del texto contra los fondos de la marca) y uso armónico del color. Criticá tu propio trabajo mientras construís y sacá capturas de pantalla para revisarlo si tu entorno lo permite: una imagen vale 1000 tokens. Tené presente el consejo de Chanel: antes de salir de casa, mirate al espejo y sacate un accesorio. Los creativos humanos tienen memoria y siempre intentan hacer algo nuevo, así que si tenés un lugar donde anotar rápido lo que probaste, te puede ayudar en pasadas futuras.

## Más sobre escritura en el diseño

Las palabras aparecen en un diseño por una sola razón: hacerlo más fácil de entender y de usar. Son contenido de diseño, no decoración. Aplicá al copy la misma intencionalidad y minimalismo que aplicás al espaciado y al color. Antes de escribir algo, preguntate qué necesita decir el diseño y cuál es la mejor forma de decirlo para ayudar a la persona a moverse por la experiencia.

Escribí desde la perspectiva del usuario final. Nombrá las cosas por lo que los usuarios van a entender, en lenguaje simple, no por cómo está construido el sistema. Un usuario gestiona notificaciones, no la configuración de webhooks. Describí qué es o qué hace algo en términos simples en vez de venderlo. Ser específico y legible para usuarios nuevos siempre es mejor que ser ocurrente.

Usá voz activa por defecto. Un llamado a la acción dice exactamente qué pasa al usarlo: "Guardar cambios", no "Enviar". Una acción conserva el mismo nombre a lo largo de todo el flujo, así que el botón que dice "Publicar" produce un aviso que dice "Publicado". El vocabulario de una interfaz es la señalización de quien navega el producto. La cohesión y la coherencia son la forma en que la gente aprende a moverse.

Tratá el fallo y el vacío como momentos para dar dirección, no para dar ambiente. Explicá qué salió mal y cómo arreglarlo, con la voz de la interfaz y no la de una persona. Los errores no piden perdón y nunca son vagos sobre lo que pasó. Una pantalla vacía es una invitación a actuar.

Mantené un tono conversacional: verbos simples, mayúscula solo al inicio de la oración, sin relleno, con el tono ajustado a la marca y a la audiencia. Que cada elemento escrito cumpla exactamente una función.
