import { useState, useRef } from 'react';

const ProjectCard = ({ project, isFeatured = false }) => {
    const [tilt, setTilt] = useState({ x: 0, y: 0 });
    const [isHovered, setIsHovered] = useState(false);
    const cardRef = useRef(null);

    const handleMouseMove = (e) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        setTilt({ x: x * 10, y: -y * 10 });
    };

    const handleMouseLeave = () => {
        setTilt({ x: 0, y: 0 });
        setIsHovered(false);
    };

    return (
        <div
            ref={cardRef}
            className={`relative group rounded-3xl transition-all duration-300 ease-out cursor-pointer overflow-hidden
        bg-white/5 backdrop-blur-md border border-white/10 hover:border-cyan-400/40
        ${isFeatured ? 'md:col-span-2 md:row-span-1' : ''}
        ${isHovered ? 'shadow-[0_20px_50px_rgba(0,0,0,0.5)] -translate-y-3 scale-[1.02]' : ''}`}
            style={{
                transform: `perspective(2000px) rotateX(${tilt.y}deg) rotateY(${tilt.x}deg) scale(${isHovered ? 1.02 : 1})`,
                transformStyle: 'preserve-3d',
            }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
        >
            {/* Background Glow */}
            <div
                className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500 pointer-events-none"
                style={{
                    background: `radial-gradient(circle at center, ${project.color}, transparent 80%)`
                }}
            />

            {/* Image Section */}
            <div className="relative h-64 w-full overflow-hidden">
                <div
                    className="absolute inset-0 bg-cover bg-center transition-transform duration-700 ease-out"
                    style={{
                        backgroundImage: `url(${project.image})`,
                        transform: isHovered ? 'scale(1.1)' : 'scale(1)'
                    }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent opacity-80" />

                {/* Tech Stack Tags */}
                <div className="absolute top-4 left-4 flex flex-wrap gap-2">
                    {project.tags?.map((tag, i) => (
                        <span
                            key={i}
                            className="px-3 py-1 text-[10px] font-bold tracking-widest uppercase rounded-full bg-black/50 backdrop-blur-md border border-white/10 text-white flex items-center gap-1.5"
                            style={{ borderColor: isHovered ? `${project.color}44` : 'rgba(255,255,255,0.1)' }}
                        >
                            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: project.color }} />
                            {tag}
                        </span>
                    ))}
                </div>
            </div>

            {/* Content Section */}
            <div className="p-8 relative">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h4 className="text-cyan-400 text-xs font-bold uppercase tracking-widest mb-1">{project.subtitle}</h4>
                        <h3 className="text-2xl font-bold text-white group-hover:text-white transition-colors capitalize">{project.title}</h3>
                    </div>
                </div>

                <p className="text-gray-400 text-sm leading-relaxed mb-8 line-clamp-2">
                    {project.description}
                </p>

                {/* Action Buttons */}
                <div className="flex items-center gap-4">
                    <a
                        href={project.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 py-3 text-center text-sm font-bold rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all active:scale-95"
                    >
                        GitHub
                    </a>
                    <a
                        href={project.demo}
                        className="flex-1 py-3 text-center text-sm font-bold rounded-xl bg-white text-black hover:opacity-90 transition-all active:scale-95 shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                        style={{
                            backgroundColor: project.color,
                            color: '#fff',
                            boxShadow: isHovered ? `0 0 20px ${project.color}55` : 'none'
                        }}
                    >
                        Live Demo
                    </a>
                </div>
            </div>

            {/* Internal Glow Effect */}
            <div
                className="absolute inset-0 pointer-events-none transition-opacity duration-500 rounded-3xl"
                style={{
                    border: isHovered ? `1px solid ${project.color}33` : '1px solid rgba(255,255,255,0.1)',
                    boxShadow: isHovered ? `inset 0 0 30px ${project.color}11` : 'none'
                }}
            />
        </div>
    );
};

export default ProjectCard;
