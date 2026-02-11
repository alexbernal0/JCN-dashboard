import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function Landing() {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="fixed inset-0 w-full h-full overflow-hidden bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: 'url(/landing-bg.jpg)',
      }}
    >
      {/* Clickable overlay */}
      <div 
        onClick={() => navigate('/dashboard')}
        className="absolute inset-0 flex items-center justify-center cursor-pointer"
      >
        {/* JCN.AI Text */}
        <h1 
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          className={`
            text-6xl font-light tracking-[0.3em] transition-all duration-300 select-none
            ${isHovered ? 'text-accent' : 'text-gray-800'}
          `}
          style={{
            textShadow: isHovered ? '0 0 20px rgba(59, 130, 246, 0.5)' : 'none'
          }}
        >
          JCN.AI
        </h1>
      </div>

      {/* Subtle hint text at bottom */}
      <div className="absolute bottom-8 left-0 right-0 text-center pointer-events-none">
        <p className="text-sm text-gray-500/60 font-light tracking-wider">
          Click to enter
        </p>
      </div>
    </div>
  );
}
