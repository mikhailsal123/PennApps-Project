"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { DM_Sans } from "next/font/google";

const dmSans = DM_Sans({
    subsets: ["latin"],
    weight: ["200", "500", "700"],
});

const LandingPage = () => {
    const router = useRouter();

    const handleLaunchPlatform = () => {
        router.push("/trading-platform");
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 py-12">
            {/* Header Section */}
            <div className={`${dmSans.className} text-center mb-12`}>
                <h1
                    className="text-6xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-amber-900 via-red-900 to-amber-800 bg-clip-text text-transparent"
                    style={{ fontFamily: "DM Sans, sans-serif" }}
                >
                    Trading Made Easy
                </h1>
                <p className="text-xl text-gray-600 mb-8">Become your own Hedgefund</p>
                <button
                    onClick={handleLaunchPlatform}
                    className="bg-black hover:bg-gray-800 text-white px-8 py-3 rounded-full text-lg font-medium transition-colors duration-200"
                >
                    Execute Trade
                </button>
            </div>

            {/* Code Snippets Section */}
            <div className="flex flex-col md:flex-row gap-8 max-w-6xl w-full">
                {/* Left Code Block */}
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

                {/* Right Code Block */}
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
    );
};

export default LandingPage;
