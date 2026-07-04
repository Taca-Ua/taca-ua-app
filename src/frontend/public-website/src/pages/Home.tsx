import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useEffect, useState } from 'react';
import { homepageConfigApi, type HomepageConfig } from '../api/homepageConfig';

function Home() {

  const [homepageConfig, setHomepageConfig] = useState<HomepageConfig | null>(null);

  useEffect(() => {
    const fetchHomepageConfig = async () => {
      try {
        const config = await homepageConfigApi.getHomepageConfig();
        setHomepageConfig(config);
      } catch (error) {
        console.error('Error fetching homepage config:', error);
      }
    };

    fetchHomepageConfig();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <div
        className="relative flex items-center justify-center bg-cover bg-center"
        style={{
          minHeight: 'calc(100vh - 4rem)',
          backgroundImage: `url(${homepageConfig?.hero_image_url || ''})`,
        }}
      >
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>

        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-5xl md:text-6xl font-bold mb-4">{homepageConfig?.title}</h1>
          <h2 className="text-2xl md:text-3xl font-semibold mb-6">{homepageConfig?.subtitle}</h2>
          <p className="text-xl md:text-2xl">{homepageConfig?.welcome_message}</p>
        </div>
      </div>

      <section className="py-16 px-4 md:px-8 lg:px-16 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-12 text-gray-800">
            Sobre Nós
          </h2>
          <div className="text-xl md:text-2xl text-gray-700 leading-relaxed space-y-8">
            {
              homepageConfig?.about_us.split('\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))
            }
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

      {/* Sponsors Section */}
      <section className="py-16 px-4 md:px-8 lg:px-16 bg-teal-700">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-12 text-white">
            Patrocinadores
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-items-center">
            {
              homepageConfig?.sponsors.map((sponsor, index) => (
                <a key={index} href={sponsor.website_url} target="_blank" rel="noopener noreferrer" className="w-full">
                  <div className="bg-white rounded-lg p-6 w-full h-32 flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow">
                    <img src={sponsor.logo_url} alt={sponsor.name} className="max-h-full max-w-full object-contain" />
                  </div>
                </a>
              ))
            }
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

export default Home;
