import prisma from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const { url, username, appPassword } = await req.json();

        // Get user ID
        const user = await prisma.user.findUnique({
            where: { email: session.user.email }
        });

        if (!user) return NextResponse.json({ message: "User not found" }, { status: 404 });

        const website = await prisma.website.create({
            data: {
                url,
                username,
                appPassword,
                userId: user.id
            },
        });

        return NextResponse.json(website, { status: 201 });
    } catch (error) {
        return NextResponse.json({ message: "Error creating website" }, { status: 500 });
    }
}

export async function GET(req: Request) {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const user = await prisma.user.findUnique({
        where: { email: session.user.email }
    });

    if (!user) return NextResponse.json({ message: "User not found" }, { status: 404 });

    const websites = await prisma.website.findMany({
        where: { userId: user.id }
    });

    return NextResponse.json(websites);
}
