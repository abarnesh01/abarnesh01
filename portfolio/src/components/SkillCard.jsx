import { useState, useRef, useEffect } from 'react';

const SkillCard = ({ tool }) => {
    const [tilt, setTilt] = useState({ x: 0, y: 0 });
    const [isHovered, setIsHovered] = useState(false);
    const cardRef = useRef(null);

    const iconBaseUrl = "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/";

    const handleMouseMove = (e) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        setTilt({ x: x * 20, y: -y * 20 });
    };

    const handleMouseLeave = () => {
        setTilt({ x: 0, y: 0 });
        setIsHovered(false);
    };

    return (
        <div
            ref={cardRef}
            className={`relative group p-6 rounded-2xl transition-all duration-300 ease-out cursor-pointer overflow-hidden
        bg-white/5 backdrop-blur-md border border-white/10 hover:border-cyan-400/40
        ${isHovered ? 'shadow-[0_0_20px_rgba(0,245,255,0.4)] -translate-y-3 scale-[1.02]' : ''}`}
            style={{
                transform: `perspective(1000px) rotateX(${tilt.y}deg) rotateY(${tilt.x}deg) scale(${isHovered ? 1.05 : 1})`,
                transformStyle: 'preserve-3d',
            }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
        >
            {/* Glow Effect */}
            <div
                className="absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-500 pointer-events-none"
                style={{
                    background: `radial-gradient(circle at center, ${tool.color}, transparent 70%)`
                }}
            />

            <div className="relative z-10 flex flex-col items-center text-center gap-4">
                {/* Icon Container */}
                <div className="w-16 h-16 flex items-center justify-center rounded-xl bg-white/5 p-3 group-hover:scale-110 transition-transform duration-500">
                    <img
                        src={`${iconBaseUrl}${tool.icon}`}
                        alt={tool.nama}
                        className="w-full h-full object-contain filter drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]"
                    />
                </div>

                {/* Info */}
                <div className="space-y-1">
                    <h3 className="text-lg font-bold text-white tracking-wide">{tool.nama}</h3>
                    <p className="text-xs text-cyan-400/70 uppercase tracking-widest font-medium">{tool.ket}</p>
                </div>

                {/* Progress bar */}
                <div className="w-full mt-4 space-y-2">
                    <div className="flex justify-between text-[10px] text-gray-400 font-bold uppercase tracking-tighter">
                        <span>Proficiency</span>
                        <span style={{ color: tool.color }}>{tool.level}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full transition-all duration-1000 ease-out rounded-full"
                            style={{
                                width: isHovered ? `${tool.level}%` : '0%',
                                backgroundColor: tool.color,
                                boxShadow: `0 0 10px ${tool.color}`
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SkillCard;
