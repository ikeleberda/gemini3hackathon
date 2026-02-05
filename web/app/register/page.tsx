"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { useEffect } from "react";

export default function RegisterPage() {
    const router = useRouter();

    useEffect(() => {
        const timer = setTimeout(() => {
            router.push("/login");
        }, 3000);
        return () => clearTimeout(timer);
    }, [router]);

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100">
            <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-md text-center">
                <h2 className="text-2xl font-bold text-gray-900">Registration Disabled</h2>
                <p className="text-gray-600">
                    Registration is currently closed. You will be redirected to the login page shortly.
                </p>
                <div className="mt-6">
                    <Link href="/login" className="text-indigo-600 hover:text-indigo-500 font-medium">
                        Go to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}
