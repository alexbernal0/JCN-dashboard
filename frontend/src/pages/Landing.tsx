import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export default function Landing() {
  const navigate = useNavigate();

  // Prevent scrolling on landing page
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    };
  }, []);

  return (
    <div
      onClick={() => navigate('/dashboard')}
      className="fixed inset-0 w-screen h-screen overflow-hidden cursor-pointer"
      style={{
        backgroundImage: 'url(/landing-bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* JCN.AI text positioned in the center white space */}
      <div className="absolute inset-0 flex items-center justify-center" style={{ marginTop: '-27vh' }}>
        <h1
          className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-wider transition-all duration-500 ease-in-out hover:scale-110 hover:text-[#00f0ff] hover:drop-shadow-[0_0_40px_rgba(0,240,255,0.9)]"
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
