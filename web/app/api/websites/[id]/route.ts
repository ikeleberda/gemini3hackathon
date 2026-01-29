import prisma from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function PATCH(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const { url, username, appPassword } = await req.json();
        const { id } = await params;

        const website = await prisma.website.update({
            where: { id },
            data: {
                url,
                username,
                appPassword: appPassword || undefined,
            },
        });

        return NextResponse.json(website);
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error updating website" }, { status: 500 });
    }
}

export async function DELETE(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const { id } = await params;

        await prisma.website.delete({
            where: { id },
        });

        return NextResponse.json({ message: "Website deleted" });
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error deleting website" }, { status: 500 });
    }
}
