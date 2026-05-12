import { motion } from "framer-motion";
import { User, MapPin, Target, Activity, ShieldAlert, Crosshair } from "lucide-react";

interface SubjectCardProps {
    id: string;
    label: string;
    confidence: number;
    lastSeen: string;
    threatScore: number;
    status: "tracking" | "lost" | "alert";
}

export function SubjectCard({ id, label, confidence, lastSeen, threatScore, status }: SubjectCardProps) {
    return (
        <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel-heavy p-5 border-l-2 border-red-600 relative overflow-hidden group font-inter"
        >
            <div className="absolute top-2 right-2 flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${
                    status === 'alert' ? 'bg-red-600' : status === 'tracking' ? 'bg-green-500' : 'bg-gray-600'
                }`} />
                <span className="text-[8px] font-black text-white uppercase tracking-widest">{status}</span>
            </div>

            <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 rounded-sm bg-red-950/20 border border-red-900/30 flex items-center justify-center text-red-600">
                    <User size={24} />
                </div>
                <div>
                    <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-0.5">Subject_ID</p>
                    <h3 className="text-xl font-black text-white italic tracking-tighter uppercase">{id}</h3>
                </div>
            </div>

            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 text-gray-500">
                        <Target size={12} />
                        <span className="text-[9px] font-black uppercase tracking-widest">Classification</span>
                    </div>
                    <span className="text-[10px] font-black text-white italic uppercase">{label} ({Math.round(confidence * 100)}%)</span>
                </div>

                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 text-gray-500">
                        <ShieldAlert size={12} />
                        <span className="text-[9px] font-black uppercase tracking-widest">Threat_Score</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <span className={`text-[10px] font-black italic ${threatScore > 70 ? 'text-red-500' : 'text-orange-500'}`}>
                            {threatScore}%
                        </span>
                        <div className="w-16 h-1 bg-white/5 rounded-full overflow-hidden ml-2">
                            <motion.div 
                                initial={{ width: 0 }}
                                animate={{ width: `${threatScore}%` }}
                                className={`h-full ${threatScore > 70 ? 'bg-red-600' : 'bg-orange-500'}`}
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 text-gray-500">
                        <MapPin size={12} />
                        <span className="text-[9px] font-black uppercase tracking-widest">Last_Known_Node</span>
                    </div>
                    <span className="text-[10px] font-black text-white italic uppercase">{lastSeen}</span>
                </div>
            </div>

            <div className="mt-6 pt-4 border-t border-white/5 flex gap-2">
                <button className="flex-1 py-2 bg-red-600 text-white text-[9px] font-black uppercase tracking-widest hover:bg-red-500 transition-all flex items-center justify-center gap-2">
                    <Crosshair size={12} /> Target_Lock
                </button>
                <button className="p-2 bg-white/5 border border-white/10 text-gray-400 hover:text-white transition-colors">
                    <Activity size={14} />
                </button>
            </div>
            
            <div className="absolute -right-4 -bottom-4 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
                <Target size={120} className="text-red-600" />
            </div>
        </motion.div>
    );
}
