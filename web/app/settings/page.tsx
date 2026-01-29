"use client";

import { useState, useEffect } from "react";
import { Cpu, ArrowLeft, Save, Key } from "lucide-react";
import Link from "next/link";

export default function SettingsPage() {
    const [googleApiKey, setGoogleApiKey] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState({ text: "", type: "" });

    useEffect(() => {
        fetch("/api/user/settings")
            .then((res) => res.json())
            .then((data) => {
                if (data.googleApiKey) {
                    setGoogleApiKey(data.googleApiKey);
                }
                setIsLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setIsLoading(false);
            });
    }, []);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage({ text: "", type: "" });

        try {
            const res = await fetch("/api/user/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ googleApiKey }),
            });

            if (res.ok) {
                setMessage({ text: "Settings saved successfully!", type: "success" });
            } else {
                setMessage({ text: "Failed to save settings.", type: "error" });
            }
        } catch (err) {
            setMessage({ text: "An error occurred.", type: "error" });
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900">
            <nav className="bg-white border-b border-gray-200">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 justify-between items-center">
                        <div className="flex items-center gap-2">
                            <div className="bg-indigo-600 p-1.5 rounded-lg">
                                <Cpu className="h-5 w-5 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-tight">Content<span className="text-indigo-600">AI</span></span>
                        </div>
                        <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-700">
                            <ArrowLeft className="h-4 w-4" /> Back to Dashboard
                        </Link>
                    </div>
                </div>
            </nav>

            <main className="py-10">
                <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
                    <header className="mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
                        <p className="mt-2 text-sm text-gray-600">Configure your autonomous content marketing credentials.</p>
                    </header>

                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                        <form onSubmit={handleSave} className="p-6 space-y-6">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                    <Key className="h-5 w-5 text-indigo-600" />
                                    AI Credentials
                                </h3>
                                <div className="space-y-4">
                                    <div>
                                        <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700">
                                            Google Gemini API Key
                                        </label>
                                        <p className="mt-1 text-xs text-gray-500 mb-2">
                                            Required for content generation and image creation. You can get one from the <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">Google AI Studio</a>.
                                        </p>
                                        <input
                                            type="password"
                                            id="apiKey"
                                            value={googleApiKey}
                                            onChange={(e) => setGoogleApiKey(e.target.value)}
                                            className="block w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                            placeholder="Enter your Google API prompt..."
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            {message.text && (
                                <div className={`p-4 rounded-lg text-sm ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                                    {message.text}
                                </div>
                            )}

                            <div className="pt-4 border-t border-gray-100 flex justify-end">
                                <button
                                    type="submit"
                                    disabled={isSaving}
                                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    {isSaving ? (
                                        <>
                                            <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <Save className="h-4 w-4" />
                                            Save Settings
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>

                    <div className="mt-8 p-4 rounded-xl bg-orange-50 border border-orange-100">
                        <div className="flex gap-3">
                            <div className="bg-orange-100 p-2 rounded-lg h-fit">
                                <Cpu className="h-5 w-5 text-orange-600" />
                            </div>
                            <div>
                                <h4 className="text-sm font-semibold text-orange-900">Privacy Notice</h4>
                                <p className="mt-1 text-sm text-orange-800 leading-relaxed">
                                    Your API keys are stored securely in our database and are used only to power the AI agents for your content creation tasks. We do not share these keys with any third parties.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
