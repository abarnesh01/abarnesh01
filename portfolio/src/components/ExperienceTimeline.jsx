import React from 'react';
import { motion, useScroll, useSpring } from 'framer-motion';

const timelineData = [
    {
        title: "Projects Development",
        subtitle: "AI & Cybersecurity Tools",
        date: "Current",
        description: "Building high-performance cybersecurity solutions including PII masking tools, network monitors, and AI surveillance systems.",
        icon: "🚀"
    },
    {
        title: "Cisco Certification",
        subtitle: "Networking & Security",
        date: "2024",
        description: "Mastered network protocols, firewall configurations, and secure infrastructure design through Cisco's industry-standard curriculum.",
        icon: "🛡️"
    },
    {
        title: "Google Certification",
        subtitle: "Cybersecurity Analyst",
        date: "2024",
        description: "Completed professional cybersecurity training focused on threat intelligence, risk management, and incident response.",
        icon: "🔍"
    },
    {
        title: "CTF Competitor",
        subtitle: "Ethical Hacking",
        date: "2023 - Present",
        description: "Regularly participating in Capture The Flag competitions, solving complex puzzles in web security, cryptography, and forensics.",
        icon: "🏆"
    },
    {
        title: "Cybersecurity Student",
        subtitle: "KGiSL Institute",
        date: "2022 - Present",
        description: "Specializing in information security, system architecture, and advanced threat detection at the KGiSL Institute of Technology.",
        icon: "🎓"
    }
];

const TimelineCard = ({ item, index }) => {
    const isEven = index % 2 === 0;

    return (
        <div className={`mb-12 flex justify-between items-center w-full ${isEven ? 'flex-row-reverse' : 'flex-row'}`}>
            <div className="hidden md:block w-5/12" />

            <div className="z-20">
                <div className="flex items-center justify-center w-12 h-12 rounded-full bg-[#050505] border-2 border-[#00f5ff] shadow-[0_0_15px_rgba(0,245,255,0.4)] text-xl">
                    {item.icon}
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0, x: isEven ? 50 : -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="w-full md:w-5/12 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-[#00f5ff]/50 transition-colors group shadow-2xl relative overflow-hidden"
            >
                {/* Glow accent */}
                <div className="absolute top-0 right-0 w-24 h-24 bg-[#00f5ff]/5 blur-3xl rounded-full" />

                <span className="text-[#00f5ff] font-mono text-sm mb-2 block">{item.date}</span>
                <h3 className="text-xl font-bold text-white mb-1 group-hover:text-[#00f5ff] transition-colors">{item.title}</h3>
                <p className="text-[#8a2be2] text-sm font-semibold mb-3">{item.subtitle}</p>
                <p className="text-gray-400 text-sm leading-relaxed">{item.description}</p>
            </motion.div>
        </div>
    );
};

const ExperienceTimeline = () => {
    const { scrollYProgress } = useScroll();
    const scaleY = useSpring(scrollYProgress, {
        stiffness: 100,
        damping: 30,
        restDelta: 0.001
    });

    return (
        <div className="relative max-w-6xl mx-auto px-4 py-20">
            <div className="text-center mb-20">
                <h2 className="text-4xl md:text-6xl font-black mb-4 text-white">
                    System <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">Timeline</span>
                </h2>
                <p className="text-gray-400 max-w-xl mx-auto">
                    Tracking career progression and technical evolution through the digital landscape.
                </p>
            </div>

            <div className="relative overflow-hidden">
                {/* Glowing Center Line */}
                <motion.div
                    className="absolute left-6 md:left-1/2 md:-translate-x-1/2 top-0 w-1 rounded-full bg-gradient-to-b from-[#8a2be2] via-[#00f5ff] to-[#8a2be2] origin-top"
                    style={{ height: '100%', scaleY }}
                />

                {/* Background glow for the line */}
                <div className="absolute left-6 md:left-1/2 md:-translate-x-1/2 top-0 w-4 h-full bg-cyan-500/10 blur-xl -z-10" />

                <div className="relative">
                    {timelineData.map((item, index) => (
                        <TimelineCard key={index} item={item} index={index} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ExperienceTimeline;
