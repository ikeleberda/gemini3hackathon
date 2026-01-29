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
        const { title, topic, scheduledFor, websiteId } = await req.json();

        // Validate website ownership
        const website = await prisma.website.findUnique({
            where: { id: websiteId },
            include: { user: true }
        });

        if (!website || website.user.email !== session.user.email) {
            return NextResponse.json({ message: "Invalid website" }, { status: 403 });
        }

        const content = await prisma.contentItem.create({
            data: {
                title: title || topic,
                topic,
                scheduledFor: scheduledFor ? new Date(scheduledFor) : null,
                websiteId,
                status: "SCHEDULED"
            },
        });

        return NextResponse.json(content, { status: 201 });
    } catch (error) {
        return NextResponse.json({ message: "Error creating content" }, { status: 500 });
    }
}

export async function GET(req: Request) {
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    // Get all content items for user's websites
    const user = await prisma.user.findUnique({
        where: { email: session.user.email },
        include: {
            websites: {
                include: {
                    content: {
                        include: {
                            jobs: {
                                select: {
                                    id: true,
                                    status: true,
                                    currentStep: true,
                                    contentItemId: true,
                                    createdAt: true,
                                    updatedAt: true,
                                    // logs: false -- intentionally omitted
                                },
                                orderBy: { createdAt: 'desc' },
                                take: 1
                            }
                        }
                    }
                }
            }
        }
    });

    if (!user) return NextResponse.json({ message: "User not found" }, { status: 404 });

    // Flatten logic with type safety
    const allContent = (user as any).websites?.flatMap((w: any) => w.content) || [];

    return NextResponse.json(allContent);
}
