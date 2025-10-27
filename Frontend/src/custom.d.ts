// Declara módulos para archivos de imagen (.png, .jpg, .jpeg, .gif, .webp, .svg, etc.)
// Esto le dice a TypeScript que, cuando se importa un archivo con estas extensiones,
// debe tratar el módulo como una cadena (string), que es la URL de la imagen.
declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.svg' {
  const content: string;
  export default content;
}