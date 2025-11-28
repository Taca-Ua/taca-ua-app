import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Home() {
  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section with Background Image */}
      <div 
        className="relative flex items-center justify-center bg-cover bg-center"
        style={{ 
          minHeight: 'calc(100vh - 4rem)',
          backgroundImage: 'url(/ab204667-c021-499c-b1f9-db300bfd877c.webp)',
        }}
      >
        {/* Overlay for blur/darkness effect */}
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        
        {/* Content */}
        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-5xl md:text-6xl font-bold mb-4">TACA UA</h1>
          <p className="text-xl md:text-2xl">Bem-vindo ao portal dos desportos universitários</p>
        </div>
      </div>

      {/* Sobre Nós Section */}
      <section className="py-16 px-4 md:px-8 lg:px-16 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-12 text-gray-800">
            Sobre Nós
          </h2>
          <div className="text-xl md:text-2xl text-gray-700 leading-relaxed space-y-8">
            <p>
              Somos uma plataforma dedicada a fornecer informações completas e atualizadas sobre o mundo dos desportos. 
              Nossa missão é conectar fãs, atletas e organizadores através de dados precisos e de fácil acesso.
            </p>
            <p>
              A Taça UA é o principal evento desportivo da Universidade de Aveiro, reunindo estudantes de diferentes 
              cursos numa celebração do espírito competitivo e da camaradagem universitária.
            </p>
            <p>
              Acompanhe as classificações em tempo real, consulte calendários de jogos, conheça as modalidades 
              disponíveis e fique por dentro de todos os regulamentos. Aqui encontrará tudo o que precisa para 
              acompanhar a emoção do desporto universitário.
            </p>
          </div>
        </div>
      </section>

      {/* Wave Divider */}
      <div className="relative h-24 bg-white">
        <svg
          className="absolute bottom-0 w-full h-24"
          viewBox="0 0 1440 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="none"
        >
          <path
            d="M0,64 C240,100 480,120 720,100 C960,80 1200,40 1440,64 L1440,120 L0,120 Z"
            fill="#14b8a6"
            fillOpacity="0.2"
          />
          <path
            d="M0,80 C240,50 480,40 720,60 C960,80 1200,100 1440,80 L1440,120 L0,120 Z"
            fill="#14b8a6"
            fillOpacity="0.4"
          />
          <path
            d="M0,96 C240,86 480,76 720,86 C960,96 1200,106 1440,96 L1440,120 L0,120 Z"
            fill="#0d9488"
          />
        </svg>
      </div>

      {/* Sponsors Section - Coming Soon */}
      <section className="py-16 px-4 md:px-8 lg:px-16 bg-teal-700">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-12 text-white">
            Patrocinadores
          </h2>
          <div className="text-center text-white text-xl">
            {/* Sponsors will be added here */}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

export default Home;
