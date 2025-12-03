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
  const [displayedText, setDisplayedText] = useState("");
  
  const fullText = "Bienvenido al Sistema de Gestión";
  
  // Duración total antes de que el formulario aparezca
  const totalDuration = typingDuration + blinkDuration;

  // Efecto de máquina de escribir
  useEffect(() => {
    const charDelay = typingDuration / fullText.length;
    let currentIndex = 0;
    
    const typingInterval = setInterval(() => {
      if (currentIndex < fullText.length) {
        setDisplayedText(fullText.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(typingInterval);
      }
    }, charDelay);

    return () => clearInterval(typingInterval);
  }, [typingDuration]);

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
        
        <h1 className="text-3xl md:text-4xl font-mono font-bold text-orange-700">
          {displayedText}
          <span className="animate-pulse border-r-4 border-orange-600 ml-1">&nbsp;</span>
        </h1>
        
      </div>
    </div>
  );
}