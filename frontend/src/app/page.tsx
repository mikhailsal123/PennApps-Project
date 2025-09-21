"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { DM_Sans } from "next/font/google";
import { TypingAnimation } from "./components/ui/typing-animation";

const dmSans = DM_Sans({
    subsets: ["latin"],
    weight: ["200", "500", "700"],
});

const LandingPage = () => {
    const router = useRouter();
    const [animationKey, setAnimationKey] = useState(0);
    const [showTradingPlatform, setShowTradingPlatform] = useState(false);

    const handleLaunchPlatform = () => {
        setShowTradingPlatform(true);
    };

    // Reset animation every 15 seconds (adjust timing as needed)
    useEffect(() => {
        const interval = setInterval(() => {
            setAnimationKey((prev) => prev + 1);
        }, 13000);

        return () => clearInterval(interval);
    }, []);

    const codeLines = [
        { content: "// Typing in your trade", className: "text-gray-400 mb-4" },
        { content: "if NVDA price < 180:", className: "text-blue-400" },
        { content: " { ", className: "text-white" },
        { content: "    buy 15 NVDA", className: "text-purple-400" },
        { content: " } ", className: "text-white" },
        { content: "", className: "text-blue-400" },
        { content: "if AMZN growth < 0.1 and AMZN price > 180:", className: "text-green-400" },
        { content: "{", className: "text-blue-400 mt-4" },
        { content: "    sell 10 AMZN", className: "text-yellow-400" },
        { content: "}", className: "text-white" },

        { content: "transition", className: "text-purple-400 ml-12 mt-1" },
        { content: "={{ ", className: "text-white" },
        { content: "ease:", className: "text-blue-400" },
        { content: ' "easeOut"', className: "text-green-400" },
        { content: " }}", className: "text-white" },
        { content: "animate", className: "text-purple-400 ml-12 mt-1" },
        { content: "={{ ", className: "text-white" },
        { content: "rotate:", className: "text-blue-400" },
        { content: " 360", className: "text-green-400" },
        { content: " }}", className: "text-white" },
        { content: "/>", className: "text-white ml-8 mt-1" },
        { content: ");", className: "text-white ml-4 mt-2" },
        { content: "}", className: "text-white mt-2" },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            {!showTradingPlatform ? (
                <div className="flex flex-col items-center justify-center px-4 py-12">
                    {/* Header Section */}
                    <div className={`${dmSans.className} text-center mb-12`}>
                        <h1
                            className={`${dmSans.className} text-6xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-amber-900 via-red-900 to-amber-800 bg-clip-text text-transparent pb-2 leading-tight`}
                        >
                            Trading Made Easy
                        </h1>
                        <p className="text-xl text-gray-600 mb-8 bg-transparent">Become your own Hedge Fund</p>
                        <button
                            onClick={handleLaunchPlatform}
                            className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-full text-lg font-medium transition-colors duration-200"
                        >
                            Execute Trades
                        </button>
                    </div>

                    {/* Code Snippets Section */}
                    <div className="flex flex-col md:flex-row gap-8 max-w-6xl w-full">
                        {/* Left Code Block with Typing Animation */}
                        <div className="flex-1">
                            <div className="bg-gray-900 rounded-2xl p-6 h-96 font-mono text-sm overflow-hidden">
                                <TypingAnimation
                                    key={animationKey}
                                    className="text-white text-sm font-mono text-left whitespace-pre-line"
                                    duration={100}
                                >
                                    {codeLines
                                        .map((line, index) => `${line.content}${index < codeLines.length - 1 ? "\n" : ""}`)
                                        .join("")}
                                </TypingAnimation>
                            </div>
                        </div>

                        {/* Right Code Block - Static */}
                        <div className="flex-1">
                            <div className="bg-gray-900 rounded-2xl p-6 h-96 font-mono text-sm overflow-hidden">
                                <div className="text-gray-400 mb-4">// Paste a code snippet</div>
                                <div className="text-blue-400">import</div>
                                <div className="text-white"> &#123; </div>
                                <div className="text-purple-400">motion</div>
                                <div className="text-white"> &#125; </div>
                                <div className="text-blue-400">from</div>
                                <div className="text-green-400"> "framer-motion"</div>

                                <div className="mt-4">
                                    <div className="text-blue-400">function</div>
                                    <div className="text-yellow-400"> Component</div>
                                    <div className="text-white">() &#123;</div>
                                </div>

                                <div className="ml-4 mt-2">
                                    <div className="text-blue-400">return</div>
                                    <div className="text-white"> (</div>
                                </div>

                                <div className="ml-8 mt-2">
                                    <div className="text-white">&lt;</div>
                                    <div className="text-red-400">motion.div</div>
                                </div>

                                <div className="ml-12 mt-1">
                                    <div className="text-purple-400">transition</div>
                                    <div className="text-white">=&#123;&#123; </div>
                                    <div className="text-blue-400">ease:</div>
                                    <div className="text-green-400"> "easeOut"</div>
                                    <div className="text-white"> &#125;&#125;</div>
                                </div>

                                <div className="ml-12 mt-1">
                                    <div className="text-purple-400">animate</div>
                                    <div className="text-white">=&#123;&#123; </div>
                                    <div className="text-blue-400">rotate:</div>
                                    <div className="text-green-400"> 360</div>
                                    <div className="text-white"> &#125;&#125;</div>
                                </div>

                                <div className="ml-8 mt-1">
                                    <div className="text-white">/&gt;</div>
                                </div>

                                <div className="ml-4 mt-2">
                                    <div className="text-white">);</div>
                                </div>

                                <div className="mt-2">
                                    <div className="text-white">&#125;</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                /* Trading Platform iframe */
                <div className="h-screen flex flex-col">
                    {/* Header with back button */}
                    <div className="bg-white shadow-sm border-b px-6 py-4 flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => setShowTradingPlatform(false)}
                                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                </svg>
                                <span>Back to Landing</span>
                            </button>
                            <h2 className="text-xl font-semibold text-gray-800">Portfolio Trading Platform</h2>
                        </div>
                        <div className="text-sm text-gray-500">
                            Powered by Flask Backend
                        </div>
                    </div>
                    
                    {/* iframe container */}
                    <div className="flex-1 bg-gray-100">
                        <iframe
                            src="http://localhost:5002"
                            className="w-full h-full border-0"
                            title="Portfolio Trading Platform"
                            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-top-navigation"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default LandingPage;