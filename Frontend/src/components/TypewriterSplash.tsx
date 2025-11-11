import { useState, useEffect } from "react";

interface TypewriterSplashProps {
  onAnimationEnd: () => void;
  // Duración de la animación de escritura definida en index.css (3000ms en el ejemplo)
  typingDuration?: number; 
  // Duración adicional para que el cursor parpadee un poco antes de desaparecer
  blinkDuration?: number; 
}

export function TypewriterSplash({ onAnimationEnd, typingDuration = 3000, blinkDuration = 1000 }: TypewriterSplashProps) {
  
  const [isFading, setIsFading] = useState(false);
  
  // Duración total antes de que el formulario aparezca
  const totalDuration = typingDuration + blinkDuration;

  useEffect(() => {
    // 1. Inicia el desvanecimiento del splash (fade-out)
    const fadeTimer = setTimeout(() => {
      setIsFading(true);
    }, totalDuration - 500); // Empieza 500ms antes de terminar

    // 2. Notifica al componente padre para que muestre el formulario
    const endTimer = setTimeout(() => {
      onAnimationEnd();
    }, totalDuration);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(endTimer);
    };
  }, [totalDuration, onAnimationEnd]);

  return (
    <div
      // Contenedor principal
      className={`fixed inset-0 flex items-center justify-center bg-gradient-to-br from-orange-50 to-amber-50 
        transition-opacity duration-500 ease-in-out z-[100] ${isFading ? 'opacity-0' : 'opacity-100'}`}
    >
      <div className="text-center p-6 bg-white/70 rounded-xl shadow-2xl backdrop-blur-sm">
        
        {/*
          APLICAMOS EL EFECTO DE MÁQUINA DE ESCRIBIR
          El texto es: "Bienvenido al Sistema de Gestión" (29 caracteres, ajusta --type-steps si lo cambias)
          
          Nota: En el CSS de ejemplo yo usé 25, si usas este texto, debes cambiarlo a 29
          en el index.css: --type-steps: 29; 
        */}
        <h1 
          className="typewriter text-3xl md:text-4xl font-mono font-bold text-orange-700 mx-auto"
          style={{ 
            // Esto es importante: asegurar que la animación del cursor empiece
            // justo después de que la escritura termine.
            animationDelay: `${typingDuration / 1000}s, 0s` 
          }}
        >
          Bienvenido al Sistema de Gestión
        </h1>
        
      </div>
    </div>
  );
}