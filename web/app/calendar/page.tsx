"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import HydrationSafeDate from "@/components/HydrationSafeDate";

export default function CalendarPage() {
    const [contentItems, setContentItems] = useState<any[]>([]);
    const [websites, setWebsites] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [newItem, setNewItem] = useState({ topic: "", scheduledFor: "", websiteId: "" });
    const [editingItemId, setEditingItemId] = useState<string | null>(null);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        const [cRes, wRes] = await Promise.all([
            fetch("/api/calendar"),
            fetch("/api/websites")
        ]);
        if (cRes.ok && wRes.ok) {
            const content = await cRes.json();
            setContentItems(content);
            setWebsites(await wRes.json());
        }
        setLoading(false);
    };

    const handleAddItem = async (e: React.FormEvent) => {
        e.preventDefault();

        let scheduledIso = "";
        if (newItem.scheduledFor) {
            const date = new Date(newItem.scheduledFor);
            scheduledIso = date.toISOString();
        }

        const method = editingItemId ? "PUT" : "POST";
        const body: any = {
            ...newItem,
            scheduledFor: scheduledIso
        };
        if (editingItemId) body.id = editingItemId;

        const res = await fetch("/api/calendar", {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        if (res.ok) {
            setNewItem({ topic: "", scheduledFor: "", websiteId: "" });
            setEditingItemId(null);
            fetchData();
        } else {
            alert("Failed to save content item");
        }
    };

    const handleEditStart = (item: any) => {
        setEditingItemId(item.id);

        // Convert ISO to datetime-local format (YYYY-MM-DDTHH:mm)
        // Need to handle timezone conversion to local time string properly for the input
        let scheduledLocal = "";
        if (item.scheduledFor) {
            const d = new Date(item.scheduledFor);
            const offsetMs = d.getTimezoneOffset() * 60 * 1000;
            const localDate = new Date(d.getTime() - offsetMs);
            scheduledLocal = localDate.toISOString().slice(0, 16);
        }

        setNewItem({
            topic: item.topic,
            scheduledFor: scheduledLocal,
            websiteId: item.websiteId
        });
    };

    const handleCancelEdit = () => {
        setEditingItemId(null);
        setNewItem({ topic: "", scheduledFor: "", websiteId: "" });
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this scheduled item? This cannot be undone.")) return;

        const res = await fetch(`/api/calendar?id=${id}`, {
            method: "DELETE"
        });

        if (res.ok) {
            fetchData();
            if (editingItemId === id) handleCancelEdit();
        } else {
            alert("Failed to delete item");
        }
    };

    const triggerAgent = async (itemId: string) => {
        const res = await fetch("/api/run-agent", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ contentId: itemId })
        });
        if (res.ok) {
            const data = await res.json();
            alert("Agent started!");
            fetchData();
        } else {
            alert("Failed to start agent");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-10">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="md:flex md:items-center md:justify-between">
                    <div className="min-w-0 flex-1">
                        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                            Content Calendar
                        </h2>
                        <div className="mt-2 text-sm text-gray-500"><Link href="/" className="text-indigo-600 hover:text-indigo-500">&larr; Back to Dashboard</Link></div>
                    </div>
                </div>

                <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
                    {/* List */}
                    <div className="space-y-6">
                        <div className="overflow-hidden rounded-lg bg-white shadow">
                            <div className="px-4 py-5 sm:p-6">
                                <h3 className="text-base font-semibold leading-6 text-gray-900">Scheduled Content</h3>
                                {loading ? <p>Loading...</p> : (
                                    <ul role="list" className="divide-y divide-gray-100 mt-4">
                                        {contentItems.length === 0 && <p className="text-gray-500 text-sm">No content scheduled.</p>}
                                        {contentItems.map((item) => {
                                            const latestJob = item.jobs?.[0];
                                            return (
                                                <li key={item.id} className="flex justify-between gap-x-6 py-5">
                                                    <div className="flex min-w-0 gap-x-4">
                                                        <div className="min-w-0 flex-auto">
                                                            <p className="text-sm font-semibold leading-6 text-gray-900">{item.title}</p>
                                                            <div className="mt-1 flex items-center gap-x-2 text-xs leading-5 text-gray-500">
                                                                <HydrationSafeDate date={item.scheduledFor} mode="datetime" options={{ month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }} />
                                                                <span>&bull;</span>
                                                                <span className={`font-medium ${item.status === 'PUBLISHED' ? 'text-green-600' : item.status === 'DRAFT' ? 'text-yellow-600' : 'text-orange-600'}`}>{item.status}</span>
                                                                {latestJob && latestJob.status === 'RUNNING' && latestJob.currentStep && (
                                                                    <span className="text-indigo-500 italic flex items-center gap-1.5">
                                                                        <span className="flex h-2 w-2 relative">
                                                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                                                                            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                                                                        </span>
                                                                        {latestJob.currentStep}
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="shrink-0 flex flex-col items-end gap-y-2">
                                                        {!item.publishedUrl && (
                                                            <div className="flex gap-2">
                                                                <button
                                                                    onClick={() => handleEditStart(item)}
                                                                    className="text-xs font-semibold text-gray-600 hover:text-indigo-600"
                                                                >
                                                                    Edit
                                                                </button>
                                                                <button
                                                                    onClick={() => handleDelete(item.id)}
                                                                    className="text-xs font-semibold text-red-600 hover:text-red-900"
                                                                >
                                                                    Delete
                                                                </button>
                                                                <button
                                                                    onClick={() => triggerAgent(item.id)}
                                                                    disabled={latestJob?.status === 'RUNNING' || latestJob?.status === 'PENDING'}
                                                                    className={`text-sm font-semibold ml-2 ${(latestJob?.status === 'RUNNING' || latestJob?.status === 'PENDING')
                                                                        ? 'text-gray-400 cursor-not-allowed'
                                                                        : 'text-indigo-600 hover:text-indigo-900'
                                                                        }`}
                                                                >
                                                                    {latestJob?.status === 'RUNNING' ? 'Running...' :
                                                                        latestJob?.status === 'PENDING' ? 'Pending...' : 'Run Now'}
                                                                </button>
                                                            </div>
                                                        )}
                                                        {item.publishedUrl && (
                                                            <a href={item.publishedUrl} target="_blank" rel="noopener noreferrer" className="text-green-600 hover:text-green-900 text-sm font-semibold flex items-center gap-1">
                                                                View Post
                                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                                                            </a>
                                                        )}
                                                    </div>
                                                </li>
                                            );
                                        })}
                                    </ul>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Add/Edit Form */}
                    <div className="overflow-hidden rounded-lg bg-white shadow self-start">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-base font-semibold leading-6 text-gray-900">
                                {editingItemId ? 'Edit Scheduled Item' : 'Schedule New Post'}
                            </h3>
                            <form className="mt-5 space-y-4" onSubmit={handleAddItem}>

                                <div>
                                    <label className="block text-sm font-medium leading-6 text-gray-900">Topic (for AI)</label>
                                    <input type="text" required className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                        value={newItem.topic}
                                        onChange={e => setNewItem({ ...newItem, topic: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium leading-6 text-gray-900">Target Website</label>
                                    <select required className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                        value={newItem.websiteId}
                                        onChange={e => setNewItem({ ...newItem, websiteId: e.target.value })}
                                    >
                                        <option value="">Select a website</option>
                                        {websites.map(site => (
                                            <option key={site.id} value={site.id}>{site.url}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium leading-6 text-gray-900">Schedule Date & Time</label>
                                    <input type="datetime-local" required className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                        value={newItem.scheduledFor}
                                        onChange={e => setNewItem({ ...newItem, scheduledFor: e.target.value })}
                                    />
                                </div>
                                <div className="flex gap-2">
                                    <button type="submit" className="flex-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                                        {editingItemId ? 'Update' : 'Schedule'}
                                    </button>
                                    {editingItemId && (
                                        <button type="button" onClick={handleCancelEdit} className="flex-none rounded-md bg-gray-200 px-3 py-2 text-sm font-semibold text-gray-600 shadow-sm hover:bg-gray-300">
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </form>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}
