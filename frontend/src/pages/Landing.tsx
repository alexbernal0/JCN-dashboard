import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate('/dashboard')}
      className="relative w-screen h-screen cursor-pointer overflow-hidden"
      style={{
        backgroundImage: 'url(/landing-bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* JCN.AI Text in center */}
      <div className="absolute inset-0 flex items-center justify-center">
        <h1 
          className="text-4xl font-light tracking-[0.3em] text-gray-600/80 hover:text-gray-800/90 transition-colors duration-300"
          style={{ fontFamily: 'Inter, sans-serif' }}
        >
          JCN.AI
        </h1>
      </div>

      {/* Subtle hint text at bottom */}
      <div className="absolute bottom-8 left-0 right-0 text-center">
        <p className="text-sm text-gray-400/60 font-light tracking-wider">
          Click anywhere to enter
        </p>
      </div>
    </div>
  );
}
