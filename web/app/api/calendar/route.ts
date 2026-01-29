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

    // Sort by scheduledFor (nearest first), with nulls last
    allContent.sort((a: any, b: any) => {
        if (!a.scheduledFor && !b.scheduledFor) return 0;
        if (!a.scheduledFor) return 1;
        if (!b.scheduledFor) return -1;
        return new Date(a.scheduledFor).getTime() - new Date(b.scheduledFor).getTime();
    });

    return NextResponse.json(allContent);
}

export async function PUT(req: Request) {
    const session = await getServerSession(authOptions);
    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const { id, title, topic, scheduledFor, websiteId } = await req.json();

        // Verify ownership via website relationship
        const existingItem = await prisma.contentItem.findUnique({
            where: { id },
            include: { website: { include: { user: true } } }
        });

        if (!existingItem || existingItem.website.user.email !== session.user.email) {
            return NextResponse.json({ message: "Forbidden" }, { status: 403 });
        }

        const updated = await prisma.contentItem.update({
            where: { id },
            data: {
                title: title || topic,
                topic,
                scheduledFor: scheduledFor ? new Date(scheduledFor) : null,
                websiteId,
                // Do not update status blindly, keep existing unless specific logic needed
            }
        });

        return NextResponse.json(updated);
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error updating content" }, { status: 500 });
    }
}

export async function DELETE(req: Request) {
    const session = await getServerSession(authOptions);
    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const id = searchParams.get('id');

    if (!id) return NextResponse.json({ message: "Missing ID" }, { status: 400 });

    try {
        // Verify ownership
        const existingItem = await prisma.contentItem.findUnique({
            where: { id },
            include: { website: { include: { user: true } } }
        });

        if (!existingItem || existingItem.website.user.email !== session.user.email) {
            return NextResponse.json({ message: "Forbidden" }, { status: 403 });
        }

        // Delete associated jobs first (cascade should handle this but let's be safe/explicit if needed, 
        // usually Prisma relation actions handle it if configured, or we delete manually)
        await prisma.agentJob.deleteMany({
            where: { contentItemId: id }
        });

        await prisma.contentItem.delete({
            where: { id }
        });

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error deleting content" }, { status: 500 });
    }
}
