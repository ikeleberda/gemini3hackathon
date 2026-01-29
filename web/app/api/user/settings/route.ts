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
            }
        });

        if (!user) {
            return NextResponse.json({ message: "User not found" }, { status: 404 });
        }

        return NextResponse.json({ googleApiKey: user.googleApiKey });
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
        const { googleApiKey } = await req.json();

        await prisma.user.update({
            where: { email: session.user.email },
            data: {
                googleApiKey,
            }
        });

        return NextResponse.json({ message: "Settings updated successfully" });
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error updating settings" }, { status: 500 });
    }
}
