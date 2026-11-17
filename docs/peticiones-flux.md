# Mejoras que pediríamos a Flux (Polymath)

Cosas que hemos echado en falta al hacer perfiles y módulos para el Flux Polymath.
Probado con Polymath 1.4.5.7. Se van añadiendo según aparecen.

## Módulos (mosaic)

1. **Módulos por perfil (o por tema).** La disposición de módulos (`mosaic.json`) es
   una sola para todo. Al abrir un juego con su perfil queremos poder cambiarla; por
   ejemplo, con Diablo II dejar solo el reloj. Hoy no se puede ni desde la interfaz ni
   desde el `.flux`.
2. **API para quitar, ocultar y reordenar módulos.** La API solo permite crear
   (`addGenericTile`) y actualizar (`updateGenericTile`) los nuestros. No hay forma de
   borrarlos ni de esconder los de serie.
3. **Texto de varias líneas o rejilla en los módulos genéricos.** Cada texto es de una
   sola línea, así que no se puede hacer una tabla compacta (CPU / GPU / RAM / VRAM).

## Teclas y temas

4. **Color por tecla.** Los colores (leyenda, anillo, brillo) son de todo el tema. Para
   resaltar unas teclas concretas hemos tenido que pintar el brillo en el propio fondo,
   calibrando a mano la posición de cada tecla.
5. **Geometría de las teclas en la API.** Exponer dónde cae cada tecla en el fondo de
   1920x1080 (o al menos documentarlo) para no tener que medirla. La hemos sacado del
   contorno que dibuja la vista previa de Polymath: paso de 118,3 px, tecla de 107 px,
   primera columna en x=24.
6. **Compensar el ángulo de visión.** Las teclas tienen altura; sentado, lo que se ve a
   través de ellas está desplazado respecto a lo que hay justo debajo. Un ajuste de
   «ángulo de visión» que desplace leyendas y fondo bajo las teclas ayudaría.

## Perfiles

7. **Exportar macros en el `.flux`.** Polymath quita las macros al exportar un perfil,
   así que no se pueden compartir perfiles que las usen.

## Fondos

8. **Fondos dinámicos (HTML o Wallpaper Engine completo).** Polymath importa de
   Wallpaper Engine solo vídeo o imagen («Only basic video or image wallpapers are
   supported»). Con un fondo web se podrían pintar datos en vivo (p. ej. los globos de
   vida y maná de Diablo II) en vez de limitarse a los módulos genéricos.
9. **Módulo de imagen actualizable por la API.** Alternativa más sencilla a lo anterior:
   un tile al que se le pueda mandar un PNG.
