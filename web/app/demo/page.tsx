"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Cpu, Loader2, ArrowRight, Zap, CheckCircle, AlertTriangle } from "lucide-react";

export default function DemoPage() {
    const [topic, setTopic] = useState("");
    const [jobId, setJobId] = useState<string | null>(null);
    const [logs, setLogs] = useState<string>("");
    const [status, setStatus] = useState<"IDLE" | "RUNNING" | "COMPLETED" | "FAILED">("IDLE");
    const [publishedUrl, setPublishedUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const logsEndRef = useRef<HTMLDivElement>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) return;

        setStatus("RUNNING");
        setError(null);
        setLogs("Initializing demo run...\n");
        setPublishedUrl(null);
        setJobId(null);

        try {
            const res = await fetch("/api/demo/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic }),
            });

            if (!res.ok) {
                const err = await res.text();
                throw new Error(err || "Failed to start demo");
            }

            const data = await res.json();
            setJobId(data.jobId);
        } catch (err: any) {
            console.error(err);
            setError(err.message);
            setStatus("FAILED");
        }
    };

    // Polling effect
    useEffect(() => {
        if (!jobId || status === "COMPLETED" || status === "FAILED") return;

        const poll = async () => {
            try {
                const res = await fetch(`/api/demo/jobs/${jobId}`);
                if (!res.ok) return; // Retry next time
                const data = await res.json();

                if (data.status === "COMPLETED" || data.status === "FAILED") {
                    setStatus(data.status);
                }

                if (data.logs) {
                    setLogs(data.logs);
                    // Proactive link extraction from logs
                    const urlMatch = data.logs.match(/\[View Post\]\((https?:\/\/[^\s)]+)\)/) ||
                        data.logs.match(/SUCCESS: Post published at\s*(https?:\/\/[^\s]+)/) ||
                        data.logs.match(/SIMULATED: Post would be published at\s*(https?:\/\/[^\s]+)/);
                    if (urlMatch && !publishedUrl) {
                        setPublishedUrl(urlMatch[1]);
                    }
                }

                if (data.contentItem?.publishedUrl) {
                    setPublishedUrl(data.contentItem.publishedUrl);
                }
            } catch (error) {
                console.error("Polling error:", error);
            }
        };

        const interval = setInterval(poll, 1500); // Faster polling (1.5s)
        return () => clearInterval(interval);
    }, [jobId, status]);

    // Auto-scroll logs
    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
            {/* Navbar */}
            <nav className="bg-white border-b border-gray-200">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 justify-between items-center">
                        <div className="flex items-center gap-2">
                            <div className="bg-indigo-600 p-1.5 rounded-lg">
                                <Cpu className="h-5 w-5 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-tight text-gray-900">
                                Content<span className="text-indigo-600">AI</span>
                            </span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link href="/login" className="text-sm font-medium text-gray-700 hover:text-indigo-600">
                                Sign In
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-grow">
                <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
                            Experience Agentic AI
                        </h1>
                        <p className="text-lg text-gray-600">
                            Research, write, and optimize content automatically. Try a live demo below—no signup required.
                        </p>
                    </div>

                    {/* Input Card */}
                    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden mb-8">
                        <div className="p-8">
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
                                        What should the AI write about?
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            id="topic"
                                            value={topic}
                                            onChange={(e) => setTopic(e.target.value)}
                                            placeholder="e.g., The Future of Quantum Computing in 2026"
                                            disabled={status === "RUNNING"}
                                            className="block w-full rounded-lg border-gray-300 pl-4 pr-12 py-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-lg"
                                        />
                                        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                                            <Zap className={`h-5 w-5 ${topic ? 'text-indigo-500' : 'text-gray-400'}`} />
                                        </div>
                                    </div>
                                </div>
                                <button
                                    type="submit"
                                    disabled={status === "RUNNING" || !topic.trim()}
                                    className="w-full flex items-center justify-center rounded-lg bg-indigo-600 px-8 py-3 text-base font-semibold text-white shadow-md hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                >
                                    {status === "RUNNING" ? (
                                        <>
                                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                            Generating Content (Step: {jobId ? 'In Progress' : 'Initializing'})...
                                        </>
                                    ) : (
                                        <>
                                            Generate Demo Content
                                            <ArrowRight className="ml-2 h-5 w-5" />
                                        </>
                                    )}
                                </button>
                            </form>

                            {error && (
                                <div className="mt-4 p-4 rounded-lg bg-red-50 text-red-700 flex items-center gap-2">
                                    <AlertTriangle className="h-5 w-5" />
                                    <span>{error}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Proactive View Post Button */}
                    {publishedUrl && (
                        <div className="mb-8 p-8 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 shadow-lg text-center animate-in zoom-in-95 duration-500">
                            <div className="inline-flex items-center justify-center p-3 bg-green-100 rounded-full mb-4">
                                <CheckCircle className="h-8 w-8 text-green-600" />
                            </div>
                            <h3 className="text-2xl font-bold text-green-900 mb-2">
                                {status === "COMPLETED" ? "Success! Post is Live" : "Post Link Ready!"}
                            </h3>
                            <p className="text-green-700 mb-6 max-w-md mx-auto">
                                {status === "COMPLETED"
                                    ? "Your autonomous agent has finished its mission. The article is now live on WordPress."
                                    : "The agent is still tidying up, but you can already view the result."}
                            </p>
                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <a
                                    href={publishedUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl bg-green-600 px-8 py-4 text-lg font-bold text-white shadow-md hover:bg-green-500 hover:scale-105 active:scale-95 transition-all"
                                >
                                    <Zap className="mr-2 h-5 w-5 fill-current" />
                                    VIEW LIVE POST
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </a>
                                <button
                                    onClick={() => {
                                        navigator.clipboard.writeText(publishedUrl);
                                        alert("Link copied to clipboard!");
                                    }}
                                    className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl bg-white border-2 border-green-200 px-6 py-4 text-base font-semibold text-green-700 hover:bg-green-100 transition-all font-mono text-sm"
                                >
                                    COPY URL
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Terminal / Logs Output */}
                    {(status !== "IDLE" || logs) && (
                        <div className="bg-gray-900 rounded-xl shadow-2xl overflow-hidden border border-gray-800">
                            <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
                                <div className="flex items-center gap-2">
                                    <div className="flex gap-1.5">
                                        <div className="w-3 h-3 rounded-full bg-red-500" />
                                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                        <div className="w-3 h-3 rounded-full bg-green-500" />
                                    </div>
                                    <span className="ml-3 text-xs font-mono text-gray-400">agent-logs.txt</span>
                                </div>
                                {status === "COMPLETED" && (
                                    <span className="flex items-center gap-1.5 text-xs font-medium text-green-400">
                                        <CheckCircle className="h-3.5 w-3.5" />
                                        Complete
                                    </span>
                                )}
                            </div>
                            <div className="p-4 h-96 overflow-y-auto font-mono text-sm">
                                <pre className="whitespace-pre-wrap text-gray-300 leading-relaxed">
                                    {logs}
                                </pre>
                                {publishedUrl && (
                                    <div className="mt-4 p-3 bg-green-900/30 border border-green-500/50 rounded-lg">
                                        <p className="text-xs text-green-400 mb-1 font-sans uppercase tracking-wider font-bold">Generated Link:</p>
                                        <a href={publishedUrl} target="_blank" rel="noopener noreferrer" className="text-sm text-green-300 hover:text-green-200 underline break-all font-mono">
                                            {publishedUrl}
                                        </a>
                                    </div>
                                )}
                                <div ref={logsEndRef} />
                            </div>
                        </div>
                    )}

                    {/* Info / Limitations */}
                    <div className="mt-8 text-center text-sm text-gray-500 max-w-2xl mx-auto">
                        <p>
                            <strong>Note:</strong> This demo performs real-time research and publishing.
                            to unlock advanced models, multiple websites, and scheduling.
                        </p>
                    </div>

                </div>
            </main>
        </div>
    );
}
