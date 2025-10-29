declare module '*.svg' {
  import * as React from 'react';

  // Define que el componente SVG es un componente funcional de React
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;

  // Define que la importación por defecto (si usas la sintaxis ?react) es el componente
  const src: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  export default src;
}