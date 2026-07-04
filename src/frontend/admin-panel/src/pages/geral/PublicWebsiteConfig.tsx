import { useEffect, useState } from "react";
import AboutUsEditableText from "../../components/website-configs/AboutUsEditableText";
import AddSponsorModal from "../../components/website-configs/AddSponsorModal";
import HeroImageInputModal from "../../components/website-configs/HeroImageInputModal";
import { useModal } from "../../contexts/ModalContext";
import { plataformConfigsApi, type PlataformHomepageConfig, type Sponsor } from "../../api/plataform_configs";
import { useNotification } from "../../contexts/NotificationProvider";

const PublicWebsiteConfig = () => {
    const { pushModal } = useModal();
    const { notify } = useNotification();

    const [title, setTitle] = useState("TAÇA UA");
    const [heroBackgroundImage, setHeroBackgroundImage] = useState("/hero_image_placeholder.jpg");
    const [subtitle, setSubtitle] = useState("Glicínias Plaza");
    const [welcomeText, setWelcomeText] = useState("Bem-vindo ao portal do desporto universitário");
    const [aboutUsTextLines, setAboutUsTextLines] = useState([
        "A Taça UA - Glicínias Plaza é hoje um dos símbolos mais fortes do espírito académico aveirense. Ano após ano, mobiliza milhares de estudantes em torno da competição, da rivalidade saudável entre cursos e da paixão pelo desporto universitário. Com mais de duas décadas de história, esta iniciativa afirma-se continuamente como um espaço de crescimento, convívio e identidade, onde cada modalidade reforça o sentimento de pertença e união da comunidade.",
        "Para além disso, a Taça UA destaca-se pela sua diversidade desportiva, englobando até 8 modalidades coletivas recorrentes, bem como até 16 modalidades pontuais, que incluem formatos coletivos, de pares e individuais, permitindo a participação alargada de estudantes, durante o ano inteiro, com diferentes interesses e aptidões."
    ]);
    const [sponsors, setSponsors] = useState<Sponsor[]>([
        {
            id: 1,
            name: "Glicínias Plaza",
            logo_url: "/181_glicinias_plaza_1.png",
            website_url: "https://www.glicinias.pt/",
        },
        {
            id: 2,
            name: "Câmara Municipal de Aveiro",
            logo_url: "/cmaveiro.png",
            website_url: "https://www.cm-aveiro.pt/",
        },
        {
            id: 3,
            name: "Universidade de Aveiro",
            logo_url: "/ua.png",
            website_url: "https://www.ua.pt/",
        },
        {
            id: 4,
            name: "IPDJ",
            logo_url: "/ipdj.png",
            website_url: "https://ipdj.gov.pt/",
        },
    ]);

    useEffect(() => {
        plataformConfigsApi.getPublicHomepageConfig()
          .then((config: PlataformHomepageConfig) => {
            setTitle(config.title);
            setSubtitle(config.subtitle);
            setWelcomeText(config.welcome_message);
            setAboutUsTextLines(config.about_us.split('\n'));
            setHeroBackgroundImage(config.hero_image_url);
            setSponsors(config.sponsors);
          }).catch((error) => {
            console.error("Error fetching public homepage config:", error);
            notify("Erro ao carregar a configuração da página inicial pública.", "error");
          });
    }, []);

    const handleUpdate = ({
        title,
        subtitle,
        welcome_message,
        about_us,
        hero_image
    } : {
        title?: string,
        subtitle?: string,
        welcome_message?: string,
        about_us?: string[],
        hero_image?: File | null
    }) => {
        if (!title && !subtitle && !welcome_message && !about_us && !hero_image) {
            return;
        }

        plataformConfigsApi.updatePublicHomepageConfig({
            title,
            subtitle,
            welcome_message,
            about_us: about_us?.join('\n'),
            hero_image: hero_image || undefined,
        }).then((updatedConfig: PlataformHomepageConfig) => {
            setTitle(updatedConfig.title);
            setSubtitle(updatedConfig.subtitle);
            setWelcomeText(updatedConfig.welcome_message);
            setAboutUsTextLines(updatedConfig.about_us.split('\n'));
            setHeroBackgroundImage(updatedConfig.hero_image_url);
            notify("Configuração da página inicial pública atualizada com sucesso.", "success");
        }).catch((error) => {
            console.error("Error updating public homepage config:", error);
            notify("Erro ao atualizar a configuração da página inicial pública.", "error");
        });
    }

    const handleRemoveSponsor = (sponsorId: number) => {
        plataformConfigsApi.removeSponsor(sponsorId)
            .then(() => {
                setSponsors((prev) => prev.filter((sponsor) => sponsor.id !== sponsorId));
                notify("Patrocinador removido com sucesso.", "success");
            }).catch(() => {
              notify("Erro ao remover o patrocinador.", "error");
            })
    }

    return (
      <div className="grid place-items-center space-y-8 p-8">
        <h1 className="justify-self-start text-3xl font-bold text-gray-800">
          Configuração do Website Público
        </h1>

        {/* Preview */}
        <div className="flex-1 p-8 border border-gray-300 rounded-lg shadow-md bg-white">
          <div className="min-h-screen flex flex-col">
            {/* <Navbar /> */}

            <div
              className="relative flex items-center justify-center bg-cover bg-center"
              style={{
                minHeight: "calc(100vh - 4rem)",
                backgroundImage: `url(${heroBackgroundImage})`,
              }}
              key={heroBackgroundImage}
            >
              <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

              <div className="relative text-center text-white px-4">
                <h1
                  contentEditable
                  suppressContentEditableWarning
                  className="text-5xl md:text-6xl font-bold mb-4 border border-white/50 rounded-lg p-2"
                  onBlur={(e) => handleUpdate({ title: (e.currentTarget.textContent !== title)? e.currentTarget.textContent || "" : undefined })}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      e.currentTarget.blur();
                    }
                  }}
                >
                  {title}
                </h1>
                <h2
                  contentEditable
                  suppressContentEditableWarning
                  className="text-2xl md:text-3xl font-semibold mb-6 border border-white/50 rounded-lg p-2"
                  onBlur={(e) => handleUpdate({ subtitle: (e.currentTarget.textContent !== subtitle)? e.currentTarget.textContent || "" : undefined })}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      e.currentTarget.blur();
                    }
                  }}
                >
                  {subtitle}
                </h2>
                <p
                  contentEditable
                  suppressContentEditableWarning
                  className="text-xl md:text-2xl border border-white/50 rounded-lg p-2"
                  onBlur={(e) =>
                    handleUpdate({ welcome_message: (e.currentTarget.textContent !== welcomeText)? e.currentTarget.textContent || "" : undefined })
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      e.currentTarget.blur();
                    }
                  }}
                >
                  {welcomeText}
                </p>
              </div>

              {/* Edit Symbol */}
              <button
                className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
                onClick={() =>
                  pushModal(
                    <HeroImageInputModal onImageSelected={(img) => {
                      handleUpdate({ hero_image: img });
                    }} />,
                  )
                }
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-gray-800"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.232 5.232l3.536 3.536M9 11l6 6m-6-6l-3.536-3.536a2 2 0 00-2.828 0L3 9m0 0l6 6m-6-6l3.536 3.536a2 2 0 002.828 0L15 9"
                  />
                </svg>
              </button>
            </div>

            <section className="py-16 px-4 md:px-8 lg:px-16 bg-white">
              <div className="max-w-6xl mx-auto">
                <h2 className="text-4xl md:text-5xl font-bold text-center mb-12 text-gray-800">
                  Sobre Nós
                </h2>
                <AboutUsEditableText
                  aboutUsTextLinesState={[
                    aboutUsTextLines,
                    setAboutUsTextLines,
                  ]}
                  onAboutUsTextChange={(updatedLines) => handleUpdate({ about_us: updatedLines })}
                />
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
                  {sponsors.map((sponsor, index) => (
                    <div key={index} className="relative w-full">
                      <a
                        href={sponsor.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full"
                      >
                        <div className="bg-white rounded-lg p-6 w-full h-32 flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow">
                          <img
                            src={sponsor.logo_url}
                            alt={sponsor.name}
                            className="max-h-full max-w-full object-contain"
                          />
                        </div>
                        {/* Remove button in top-right corner of sponsor card */}
                      </a>
                      <button
                        onClick={() => handleRemoveSponsor(sponsor.id)}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors w-6 h-6 flex items-center justify-center text-sm"
                      >
                        X
                      </button>
                    </div>
                  ))}
                  <button
                    className="bg-white opacity-50 rounded-lg p-6 w-full h-32 flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow"
                    onClick={() =>
                      pushModal(
                        <AddSponsorModal
                          onCreate={(sponsor) =>
                            setSponsors((prev) => [...prev, sponsor])
                          }
                        />,
                      )
                    }
                  >
                    <span className="text-gray-700 font-semibold text-lg">
                      + Adicionar Patrocinador
                    </span>
                  </button>
                </div>
              </div>
            </section>

            {/* <Footer /> */}
          </div>
        </div>
      </div>
    );
};

export default PublicWebsiteConfig;
