import React from 'react';
import { motion } from 'framer-motion';
import CountUp from './CountUp/CountUp';

const achievements = [
    {
        title: "CTF Participation",
        value: 50,
        suffix: "+",
        icon: "🎯",
        description: "Competed in numerous Capture The Flag events worldwide, solving challenges in multiple categories.",
        color: "from-cyan-500/20 to-blue-500/20"
    },
    {
        title: "CGPA Score",
        value: 7.68,
        decimals: 2,
        icon: "⭐",
        description: "Maintained a strong academic record specializing in cybersecurity and information systems.",
        color: "from-purple-500/20 to-pink-500/20"
    },
    {
        title: "Cisco Certified",
        value: 100,
        suffix: "%",
        icon: "🛡️",
        description: "Validated expertise in network security, routing, switching, and enterprise infrastructure.",
        color: "from-green-500/20 to-emerald-500/20"
    },
    {
        title: "Google Certified",
        value: 100,
        suffix: "%",
        icon: "🔍",
        description: "Professional certification in cybersecurity analysis and threat intelligence operations.",
        color: "from-orange-500/20 to-red-500/20"
    }
];

const AchievementCard = ({ item, index }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            whileHover={{ y: -10 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className={`relative p-8 rounded-[32px] bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden group hover:border-[#00f5ff]/50 transition-all duration-500 shadow-2xl`}
        >
            {/* Dynamic Background Gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

            {/* Top Section */}
            <div className="flex justify-between items-start mb-6 relative z-10">
                <div className="w-14 h-14 flex items-center justify-center text-3xl bg-black/40 rounded-2xl shadow-xl border border-white/5">
                    {item.icon}
                </div>
                <div className="text-4xl font-black text-white group-hover:text-[#00f5ff] transition-colors">
                    <CountUp
                        from={0}
                        to={item.value}
                        separator=","
                        direction="up"
                        duration={2}
                        className="achievement-count"
                        decimals={item.decimals || 0}
                    />
                    <span className="text-xl ml-1 opacity-50">{item.suffix}</span>
                </div>
            </div>

            {/* Content */}
            <div className="relative z-10">
                <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed group-hover:text-gray-300 transition-colors">
                    {item.description}
                </p>
            </div>

            {/* Decorative Border Glow */}
            <div className="absolute inset-0 border border-transparent group-hover:border-[#00f5ff]/20 rounded-[32px] pointer-events-none transition-all duration-500" />
        </motion.div>
    );
};

const AchievementsGrid = () => {
    return (
        <div className="max-w-6xl mx-auto px-4 py-20">
            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-6xl font-black mb-4 text-white">
                    System <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">Achievements</span>
                </h2>
                <p className="text-gray-400 max-w-xl mx-auto">
                    Quantifiable milestones and verified technical credentials extracted from core modules.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {achievements.map((item, index) => (
                    <AchievementCard key={index} item={item} index={index} />
                ))}
            </div>
        </div>
    );
};

export default AchievementsGrid;
