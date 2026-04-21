'use client'

import Spline from '@splinetool/react-spline'
import React, { Suspense, useState } from 'react'

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true }
    }

    componentDidCatch(error, errorInfo) {
        console.error("Spline Error:", error, errorInfo)
    }

    render() {
        if (this.state.hasError) {
            return this.props.fallback
        }
        return this.props.children
    }
}

export default function SplineScene({ scene, className }) {
    const [hasError, setHasError] = useState(false)

    const fallbackUI = (
        <div className={`${className} bg-dark-bg/20 border border-neon-cyan/10 rounded-3xl flex items-center justify-center relative overflow-hidden group uppercase tracking-widest`}>
            <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-neon-purple/5 opacity-50" />
            <div className="text-center z-10 p-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full border border-neon-cyan/30 flex items-center justify-center animate-pulse">
                    <span className="text-neon-cyan text-2xl font-bold">3D</span>
                </div>
                <p className="text-gray-400 text-sm font-bold">Scene Ready</p>
                <p className="text-[10px] text-gray-600 mt-2">Waiting for Spline Link</p>
            </div>
            {/* Ambient Background Glow for when Spline fails */}
            <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-neon-cyan/10 rounded-full blur-3xl" />
            <div className="absolute -top-10 -left-10 w-40 h-40 bg-neon-purple/10 rounded-full blur-3xl" />
        </div>
    )

    if (hasError) return fallbackUI

    return (
        <ErrorBoundary fallback={fallbackUI}>
            <Suspense fallback={<div className="w-full h-full bg-dark-bg/50 animate-pulse rounded-3xl" />}>
                <Spline
                    scene={scene}
                    className={className}
                    onError={() => setHasError(true)}
                />
            </Suspense>
        </ErrorBoundary>
    )
}
