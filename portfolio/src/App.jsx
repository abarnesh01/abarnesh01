import { useRef, useState, useEffect } from "react";
import ProfileCard from "./components/ProfileCard/ProfileCard";
import ShinyText from "./components/ShinyText/ShinyText";
import BlurText from "./components/BlurText/BlurText";
import ScrambledText from "./components/ScrambledText/ScrambledText";
import SplitText from "./components/SplitText/SplitText";
import Lanyard from "./components/Lanyard/Lanyard";
import GlassIcons from "./components/GlassIcons/GlassIcons";
import { listTools, listProyek } from "./data";
import ChromaGrid from "./components/ChromaGrid/ChromaGrid";
import ProjectModal from "./components/ProjectModal/ProjectModal";
import Aurora from "./components/Aurora/Aurora";
import AOS from 'aos';
import SkillCard from "./components/SkillCard";
import ProjectCard from "./components/ProjectCard";
import CountUp from "./components/CountUp/CountUp";
import { FaLinkedin, FaGithub, FaEnvelope, FaPhoneAlt } from 'react-icons/fa';
import { AnimatePresence } from 'framer-motion';
import BootScreen from "./components/BootScreen";
import CustomCursor from "./components/CustomCursor";
import ExperienceTimeline from "./components/ExperienceTimeline";
import AchievementsGrid from "./components/AchievementsGrid";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import PreLoader from "./components/PreLoader";
import { playHoverSound, playClickSound } from "./utils/sounds";
import 'aos/dist/aos.css';

function App() {
  const aboutRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [isBooting, setIsBooting] = useState(true);

  const [selectedProject, setSelectedProject] = useState(null); // null = modal tertutup

  const handleProjectClick = (project) => {
    setSelectedProject(project);
  };

  const handleCloseModal = () => {
    setSelectedProject(null);
  };



  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.2 }
    );

    AOS.init({
      duration: 1000,
      once: true,
      easing: 'ease-out-cubic',
    });

    if (aboutRef.current) {
      observer.observe(aboutRef.current);
    }

    /*
    // TESLA SCROLL ANIMATION
    const sections = document.querySelectorAll("section, .tools, .proyek");
    const scrollObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show-section");
          entry.target.classList.remove("hide-section");
        }
      });
    }, { threshold: 0.1 });

    sections.forEach(sec => {
      sec.classList.add("hide-section");
      scrollObserver.observe(sec);
    });
    */

    // VOICE AI INTRO
    const handleVoiceIntro = () => {
      const msg = new SpeechSynthesisUtterance(
        "Welcome to Abarnesh portfolio. Cybersecurity engineer. System initialized."
      );
      msg.rate = 0.9;
      speechSynthesis.speak(msg);
    };
    window.addEventListener("click", handleVoiceIntro, { once: true });

    // 3D TILT CARD
    const card = document.querySelector(".hero-avatar");
    const handleTilt = (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const rotateX = -(y - rect.height / 2) / 20;
      const rotateY = (x - rect.width / 2) / 20;
      if (card) card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    };
    const resetTilt = () => {
      if (card) card.style.transform = "rotateX(0) rotateY(0)";
    };

    if (card) {
      card.addEventListener("mousemove", handleTilt);
      card.addEventListener("mouseleave", resetTilt);
    }

    // SOUND EFFECTS HANDLERS
    const handleGlobalClick = (e) => {
      const target = e.target.closest('a, button, .contact-btn, .project-card, .skill-card');
      if (target) playClickSound();
    };

    const handleGlobalHover = (e) => {
      const target = e.target.closest('a, button, .contact-btn, .project-card, .skill-card');
      if (target) playHoverSound();
    };

    window.addEventListener('click', handleGlobalClick);
    window.addEventListener('mouseover', handleGlobalHover);

    return () => {
      if (observer) observer.disconnect();
      // scrollObserver.disconnect();
      window.removeEventListener("click", handleVoiceIntro);
      window.removeEventListener('click', handleGlobalClick);
      window.removeEventListener('mouseover', handleGlobalHover);
      if (card) {
        card.removeEventListener("mousemove", handleTilt);
        card.removeEventListener("mouseleave", resetTilt);
      }
    };
  }, []);

  return (
    <>
      {/* <PreLoader /> */}
      <CustomCursor />
      <AnimatePresence>
        {/* {isBooting && <BootScreen onComplete={() => setIsBooting(false)} />} */}
      </AnimatePresence>


      <div className="absolute top-0 left-0 w-full h-full -z-10 ">
        <Aurora
          colorStops={["#0f2027", "#1F97A6", "#050505"]}
          blend={0.5}
          amplitude={1.0}
          speed={0.5}
        />
        <div id="spline-container" className="absolute inset-0 z-0 opacity-50">
          {/* <spline-viewer
            url="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
          ></spline-viewer> */}
        </div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <Navbar />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          {/* Global Ambient Glows */}
          <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
            <div className="absolute top-[10%] left-[-10%] w-[50%] h-[50%] bg-purple-900/10 blur-[150px] rounded-full" />
            <div className="absolute bottom-[20%] right-[-10%] w-[40%] h-[40%] bg-cyan-900/10 blur-[150px] rounded-full" />
          </div>

          {/* Hero Section */}
          <section id="hero" className="hero grid md:grid-cols-2 items-center pt-10 xl:gap-0 gap-6 grid-cols-1">
            <div className="animate__animated animate__fadeInUp animate__delay-3s">
              <div className="flex items-center gap-3 mb-6 bg-zinc-800 w-fit p-4 rounded-2xl">
                <img src="/assets/abarnesh1.png" className="w-10 rounded-md" />
                <q>Defend with knowledge, respond with precision.</q>
              </div>
              <h1 className="text-5xl font-bold mb-6">
                <ShinyText text="Hi I'm Abarnesh S" disabled={false} speed={3} className='custom-class' />
              </h1>
              <BlurText
                text="A passionate Cybersecurity student with hands-on experience in threat detection, anomaly detection, and PII data masking. Certified by Google and Cisco, with CTF experience and strong Linux proficiency."
                delay={150}
                animateBy="words"
                direction="top"
                className=" mb-6"
              />
              <div className="flex items-center sm:gap-4 gap-2">
                <a
                  href="/assets/CV.pdf"
                  download="Abarnesh_S_CV.pdf"
                  className="font-semibold bg-[#1a1a1a] p-4 px-6 rounded-full border border-gray-700 hover:bg-[#222] transition-all duration-300 ease-out hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)]"
                >
                  <ShinyText text="Download CV" disabled={false} speed={3} className="custom-class" />
                </a>

                <a href="#project" className="font-semibold bg-[#1a1a1a] p-4 px-6 rounded-full border border-gray-700 hover:bg-[#222] transition-all duration-300 ease-out hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)]">
                  <ShinyText text="Explore My Projects" disabled={false} speed={3} className="custom-class" />
                </a>
              </div>
            </div>
            <div className="md:ml-auto animate__animated animate__fadeInUp animate__delay-4s">
              <div className="hero-avatar transition-transform duration-300 ease-out" style={{ perspective: '1000px' }}>
                <ProfileCard
                  name="Abarnesh S"
                  title="Cybersecurity Engineer | SOC Analyst | Ethical Hacking Enthusiast"
                  handle="abarnesh"
                  status="Online"
                  contactText="Contact Me"
                  avatarUrl="/assets/abarnesh.png"
                  showUserInfo={true}
                  enableTilt={true}
                  enableMobileTilt={false}
                  onContactClick={() => console.log('Contact clicked')}
                />
              </div>
            </div>
          </section>

          {/* Experience Timeline Section */}
          <section id="experience" className="mt-32">
            <ExperienceTimeline />
          </section>

          {/* About Section */}
          <section className="mt-32 mx-auto w-full max-w-6xl relative overflow-hidden" id="about" ref={aboutRef}>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full -z-10 pointer-events-none">
              <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-purple-500/10 blur-[100px] rounded-full" />
              <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-cyan-500/10 blur-[100px] rounded-full" />
            </div>

            <div
              className="flex flex-col md:flex-row items-center gap-16 p-8 md:p-16 rounded-[40px] bg-white/5 backdrop-blur-2xl border border-white/10 shadow-2xl relative"


            >
              <div className="flex-1 space-y-8">
                <div className="space-y-4">
                  <h2 className="text-4xl md:text-6xl font-black tracking-tight text-white transition-all duration-300 hover:text-cyan-400 hover:drop-shadow-[0_0_8px_rgba(0,245,255,0.6)]">
                    About <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">Me</span>
                  </h2>
                  <div className="h-1 w-20 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full" />
                </div>

                <p className="text-gray-300 text-lg leading-relaxed font-medium">
                  I'm Abarnesh S, a Cybersecurity Engineering student at KGISL Institute of Technology.
                  I specialize in building real-world security systems, focusing on threat detection,
                  anomaly analysis, and OCR-based data masking.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4">
                  {[
                    { label: 'Projects', value: 3, suffix: '+' },
                    { label: 'Experience', value: 1, suffix: '+' },
                    { label: 'CGPA', value: 7.68, suffix: '/10' }
                  ].map((stat, i) => (
                    <div key={i} className="group p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-purple-500/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(138,43,226,0.2)]">
                      <h3 className="text-3xl font-bold text-white mb-2 flex items-baseline">
                        <CountUp to={stat.value} duration={2} separator="." decimals={stat.label === 'CGPA' ? 2 : 0} />
                        <span className="text-sm text-purple-400 ml-0.5">{stat.suffix}</span>
                      </h3>
                      <p className="text-xs uppercase tracking-widest text-gray-400 font-bold">{stat.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex-1 flex justify-center items-center">
                <div className="relative group animate-float">
                  <div className="absolute inset-0 bg-purple-500/20 blur-[60px] rounded-full group-hover:bg-cyan-500/30 transition-all duration-700" />
                  <div className="relative w-64 h-64 md:w-80 md:h-80 rounded-[40px] p-2 bg-gradient-to-br from-purple-500 to-cyan-500 shadow-2xl transition-all duration-500 hover:scale-105 hover:rotate-3 overflow-hidden">
                    <div className="w-full h-full rounded-[38px] bg-[#050505] overflow-hidden relative">
                      <img
                        src="/assets/abarnesh.png"
                        alt="Abarnesh S"
                        className="w-full h-full object-cover transition-all duration-700 group-hover:scale-110 group-hover:brightness-110"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Tools Section */}
          <section className="tools mt-32 relative py-20">
            <div className="absolute top-0 left-0 w-full h-full -z-10 pointer-events-none overflow-hidden">
              <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 blur-[120px] rounded-full" />
              <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 blur-[120px] rounded-full" />
            </div>

            <div className="text-center mb-20">
              <h1 className="text-4xl md:text-5xl font-extrabold mb-6 tracking-tight bg-gradient-to-r from-white to-gray-500 bg-clip-text text-transparent"  >
                Tools & Technologies
              </h1>
              <p className="max-w-2xl mx-auto text-base text-gray-400 leading-relaxed"   >
                A comprehensive toolkit of technologies I use to build scalable, secure, and performant digital experiences.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
              {listTools?.map((tool, index) => (
                <div
                  key={tool.id}


                  data-aos-delay={index * 50}
                >
                  <SkillCard tool={tool} />
                </div>
              ))}
            </div>
          </section>

          {/* Achievements Section */}
          <section id="achievements" className="mt-32">
            <AchievementsGrid />
          </section>

          {/* Projects Section */}
          <section className="proyek mt-32 relative py-20" id="project">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full -z-10 pointer-events-none">
              <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/5 blur-[150px] rounded-full animate-pulse" />
              <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-rose-500/5 blur-[150px] rounded-full animate-pulse" style={{ animationDelay: '2s' }} />
            </div>

            <div className="text-center mb-20 px-4">
              <h1 className="text-4xl md:text-6xl font-black mb-6 bg-gradient-to-r from-white via-white to-white/20 bg-clip-text text-transparent"  >
                Featured Projects
              </h1>
              <p className="max-w-2xl mx-auto text-base text-gray-400 leading-relaxed"   >
                A showcase of my recent cybersecurity tools and AI systems, designed with performance and security at the core.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-10">
              {listProyek?.map((project, index) => (
                <div
                  key={project.id}


                  data-aos-delay={index * 150}
                  className={index === 0 ? 'md:col-span-2' : ''}
                >
                  <ProjectCard project={project} isFeatured={index === 0} />
                </div>
              ))}
            </div>
          </section>

          {/* Contact Section */}
          <section className="kontak mt-32 relative py-20 px-4" id="contact">
            <div
              className="max-w-3xl mx-auto bg-white/5 backdrop-blur-xl border border-white/10 rounded-[32px] p-8 md:p-16 text-center shadow-2xl relative overflow-hidden"

            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 blur-3xl -z-10" />
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-purple-500/10 blur-3xl -z-10" />

              <h2 className="text-4xl md:text-6xl font-black mb-4 text-white">
                Let's <span className="text-[#00f5ff] drop-shadow-[0_0_10px_rgba(0,245,255,0.3)]">Connect</span>
              </h2>
              <p className="text-gray-400 text-lg mb-12 max-w-md mx-auto">
                Have a project or question? Feel free to reach out.
              </p>

              <div className="flex flex-wrap justify-center gap-4">
                <a
                  href="https://www.linkedin.com/in/abarnesh-s-106a34314/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="contact-btn group transition-all duration-300 ease-out hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)] hover:border-cyan-400/40"
                >
                  <FaLinkedin className="text-xl" />
                  <span>LinkedIn</span>
                </a>
                <a
                  href="https://github.com/abarnesh01"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="contact-btn group transition-all duration-300 ease-out hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)] hover:border-cyan-400/40"
                >
                  <FaGithub className="text-xl" />
                  <span>GitHub</span>
                </a>
                <a
                  href="mailto:abarnesh772@gmail.com"
                  className="contact-btn group transition-all duration-300 ease-out hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)] hover:border-cyan-400/40"
                >
                  <FaEnvelope className="text-xl" />
                  <span>Email</span>
                </a>
                <a
                  href="tel:+919944254589"
                  className="contact-btn group transition-all duration-300 ease-out hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)] hover:border-cyan-400/40"
                >
                  <FaPhoneAlt className="text-xl" />
                  <span>Phone</span>
                </a>
              </div>
            </div>
          </section>
        </main>

        <Footer />
      </div >

      <ProjectModal
        isOpen={!!selectedProject}
        onClose={handleCloseModal}
        project={selectedProject}
      />
    </>
  );
}

export default App;
