"use client";

import { useEffect, useState } from "react";

interface HydrationSafeDateProps {
    date: string | Date;
    options?: Intl.DateTimeFormatOptions;
    mode?: "date" | "time" | "datetime";
}

export default function HydrationSafeDate({ date, options, mode = "date" }: HydrationSafeDateProps) {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return <span className="invisible">Loading...</span>;
    }

    const d = new Date(date);

    if (mode === "time") {
        return <span>{d.toLocaleTimeString([], options)}</span>;
    }

    if (mode === "datetime") {
        return <span>{d.toLocaleString([], options)}</span>;
    }

    return <span>{d.toLocaleDateString([], options)}</span>;
}
