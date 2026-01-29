import prisma from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function GET() {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const user = await prisma.user.findUnique({
            where: { email: session.user.email },
            select: {
                googleApiKey: true,
                googleModelName: true,
                googleFallbackModels: true,
            } as any
        });

        if (!user) {
            return NextResponse.json({ message: "User not found" }, { status: 404 });
        }

        const userData = user as any;
        return NextResponse.json({
            googleApiKey: userData.googleApiKey,
            googleModelName: userData.googleModelName,
            googleFallbackModels: userData.googleFallbackModels,
        });
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error fetching settings" }, { status: 500 });
    }
}

export async function POST(req: Request) {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const { googleApiKey, googleModelName, googleFallbackModels } = await req.json();

        await prisma.user.update({
            where: { email: session.user.email },
            data: {
                googleApiKey,
                googleModelName,
                googleFallbackModels,
            } as any
        });

        return NextResponse.json({ message: "Settings updated successfully" });
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error updating settings" }, { status: 500 });
    }
}
