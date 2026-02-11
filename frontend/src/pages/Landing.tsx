import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate('/dashboard')}
      className="fixed inset-0 w-full h-full overflow-hidden cursor-pointer"
      style={{
        backgroundImage: 'url(/shutterstock_61843960.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* JCN.AI text positioned in the center white space */}
      <div className="absolute inset-0 flex items-center justify-center">
        <h1
          className="text-6xl md:text-8xl lg:text-9xl font-bold tracking-wider transition-all duration-300 hover:text-[#00d4ff] hover:drop-shadow-[0_0_30px_rgba(0,212,255,0.8)]"
          style={{
            color: '#1a1a1a',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 700,
            letterSpacing: '0.1em',
          }}
        >
          JCN.AI
        </h1>
      </div>
    </div>
  );
}
