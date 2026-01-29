import prisma from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function GET(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;
    const session = await getServerSession(authOptions);

    if (!session || !session.user?.email) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const job = await prisma.agentJob.findUnique({
            where: { id },
            include: {
                contentItem: {
                    include: {
                        website: {
                            include: {
                                user: true
                            }
                        }
                    }
                }
            }
        });

        if (!job) {
            return NextResponse.json({ message: "Job not found" }, { status: 404 });
        }

        // Verify website ownership
        if (job.contentItem.website.user.email !== session.user.email) {
            return NextResponse.json({ message: "Forbidden" }, { status: 403 });
        }

        // Truncate logs if too large (e.g., last 50,000 characters)
        if (job.logs && job.logs.length > 50000) {
            job.logs = "...(truncated)...\n" + job.logs.slice(-50000);
        }

        return NextResponse.json(job);
    } catch (error: any) {
        return NextResponse.json({ message: "Error fetching job", error: error.message }, { status: 500 });
    }
}
