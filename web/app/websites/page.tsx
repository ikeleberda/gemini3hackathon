"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Website {
    id: string;
    url: string;
    username: string;
}

export default function WebsitesPage() {
    const [websites, setWebsites] = useState<Website[]>([]);
    const [loading, setLoading] = useState(true);
    const [newSite, setNewSite] = useState({ url: "", username: "", appPassword: "" });

    useEffect(() => {
        fetchWebsites();
    }, []);

    const fetchWebsites = async () => {
        const res = await fetch("/api/websites");
        if (res.ok) {
            const data = await res.json();
            setWebsites(data);
        }
        setLoading(false);
    };

    const handleAddSite = async (e: React.FormEvent) => {
        e.preventDefault();
        const res = await fetch("/api/websites", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newSite)
        });

        if (res.ok) {
            setNewSite({ url: "", username: "", appPassword: "" });
            fetchWebsites();
        } else {
            alert("Failed to add website");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-10">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="md:flex md:items-center md:justify-between">
                    <div className="min-w-0 flex-1">
                        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                            Connected Websites
                        </h2>
                        <div className="mt-2 text-sm text-gray-500"><Link href="/" className="text-indigo-600 hover:text-indigo-500">&larr; Back to Dashboard</Link></div>
                    </div>
                </div>

                <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
                    {/* List */}
                    <div className="overflow-hidden rounded-lg bg-white shadow">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-base font-semibold leading-6 text-gray-900">Your Sites</h3>
                            {loading ? <p>Loading...</p> : (
                                <ul role="list" className="divide-y divide-gray-100 mt-4">
                                    {websites.length === 0 && <p className="text-gray-500 text-sm">No websites connected yet.</p>}
                                    {websites.map((site) => (
                                        <li key={site.id} className="flex justify-between gap-x-6 py-5">
                                            <div className="flex min-w-0 gap-x-4">
                                                <div className="min-w-0 flex-auto">
                                                    <p className="text-sm font-semibold leading-6 text-gray-900">{site.url}</p>
                                                    <p className="mt-1 truncate text-xs leading-5 text-gray-500">{site.username}</p>
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* Add Form */}
                    <div className="overflow-hidden rounded-lg bg-white shadow">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-base font-semibold leading-6 text-gray-900">Add New Connection</h3>
                            <form className="mt-5 space-y-4" onSubmit={handleAddSite}>
                                <div>
                                    <label className="block text-sm font-medium leading-6 text-gray-900">WordPress URL</label>
                                    <input type="url" required className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                        placeholder="https://example.com"
                                        value={newSite.url}
                                        onChange={e => setNewSite({ ...newSite, url: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium leading-6 text-gray-900">Username</label>
                                    <input type="text" required className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                        value={newSite.username}
                                        onChange={e => setNewSite({ ...newSite, username: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium leading-6 text-gray-900">Application Password</label>
                                    <input type="password" required className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                        value={newSite.appPassword}
                                        onChange={e => setNewSite({ ...newSite, appPassword: e.target.value })}
                                    />
                                </div>
                                <button type="submit" className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Connect</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
