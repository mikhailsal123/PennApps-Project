"use client";

import React, { useState } from "react";

const ThreeSectionLayout = () => {
    // State for chat history
    const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);

    // State for cards data
    const [cardsData, setCardsData] = useState([
        {
            title: "Card 1",
            content: "This is the content of the first card. It contains some sample text to demonstrate the layout.",
        },
        {
            title: "Card 2",
            content: "This is the second card with different content. You can scroll through multiple cards.",
        },
        { title: "Card 3", content: "Third card showcasing the scrollable functionality of this section." },
        { title: "Card 4", content: "Another card to demonstrate the scrolling feature when there are many cards." },
        { title: "Card 5", content: "Fifth card with more sample content to fill the scrollable area." },
        { title: "Card 6", content: "Last sample card to show how the scroll works with multiple items." },
    ]);

    // State for input forms
    const [userInput, setUserInput] = useState("");
    const [chatInput, setChatInput] = useState("");
    const [processedMessage, setProcessedMessage] = useState("");

    // Handle input processing
    const handleProcessInput = () => {
        if (userInput) {
            setProcessedMessage(`Processed: ${userInput}`);
        } else {
            setProcessedMessage("Please enter some text first!");
        }
    };

    // Handle chat message sending
    const handleSendMessage = () => {
        if (chatInput.trim()) {
            const newUserMessage = { role: "user", content: chatInput };
            const aiResponse = {
                role: "ai",
                content: `Thanks for your message: '${chatInput}'. This is a placeholder AI response.`,
            };

            setChatHistory((prev) => [...prev, newUserMessage, aiResponse]);
            setChatInput("");
        }
    };

    // Handle clearing chat
    const handleClearChat = () => {
        setChatHistory([]);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            {/* Main Title */}
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Three-Section Layout Demo</h1>

            <div className="grid grid-cols-2 grid-rows-2 gap-6 h-[calc(100vh-120px)]">
                {/* TOP LEFT QUADRANT: Input Section */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-blue-600 mb-4 flex items-center">📝 Input Section</h2>

                    <div className="space-y-4">
                        <textarea
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Enter your code here..."
                            rows={8}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-none"
                        />

                        <button
                            onClick={handleProcessInput}
                            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200"
                        >
                            Process Input
                        </button>

                        {processedMessage && (
                            <div
                                className={`p-3 rounded-md ${
                                    processedMessage.includes("Please")
                                        ? "bg-yellow-50 text-yellow-800 border border-yellow-200"
                                        : "bg-green-50 text-green-800 border border-green-200"
                                }`}
                            >
                                {processedMessage}
                            </div>
                        )}

                        {userInput && (
                            <div className="p-3 bg-blue-50 text-blue-800 border border-blue-200 rounded-md">
                                <div className="text-sm font-semibold mb-1">Current input:</div>
                                <pre className="text-xs overflow-x-auto">{userInput}</pre>
                            </div>
                        )}
                    </div>
                </div>

                {/* RIGHT SIDE - Cards section spanning two quadrants */}
                <div className="row-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-blue-600 mb-4 flex items-center">�� Cards Section</h2>

                    {/* Scrollable Cards Container */}
                    <div className="h-full overflow-y-auto border border-gray-200 rounded-md p-3 bg-gray-50">
                        <div className="space-y-3">
                            {cardsData.map((card, index) => (
                                <div
                                    key={index}
                                    className="bg-white border border-gray-200 rounded-md p-4 shadow-sm hover:shadow-md transition-shadow duration-200"
                                >
                                    <div className="font-semibold text-gray-800 mb-2">{card.title}</div>
                                    <div className="text-gray-600 text-sm">{card.content}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* BOTTOM LEFT QUADRANT: AI Chat Section */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-blue-600 mb-4 flex items-center">�� AI Chat</h2>

                    {/* Chat Display Area */}
                    <div className="h-40 overflow-y-auto border border-gray-200 rounded-md p-3 mb-4 bg-gray-50">
                        {chatHistory.length === 0 ? (
                            <div className="text-gray-500 italic">Start a conversation with the AI bot...</div>
                        ) : (
                            <div className="space-y-3">
                                {chatHistory.map((message, index) => (
                                    <div key={index} className="mb-2">
                                        <strong
                                            className={message.role === "user" ? "text-blue-600" : "text-green-600"}
                                        >
                                            {message.role === "user" ? "You:" : "AI:"}
                                        </strong>
                                        <span className="ml-2">{message.content}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Chat Input */}
                    <div className="space-y-3">
                        <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                            placeholder="Type your message here..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />

                        <div className="flex gap-2">
                            <button
                                onClick={handleSendMessage}
                                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200"
                            >
                                Send
                            </button>
                            <button
                                onClick={handleClearChat}
                                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors duration-200"
                            >
                                Clear Chat
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ThreeSectionLayout;
