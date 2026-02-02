
import prisma from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET(
    req: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;

    try {
        const job = await prisma.agentJob.findUnique({
            where: { id },
            // Only select necessary fields
            select: {
                id: true,
                status: true,
                logs: true,
                currentStep: true,
                createdAt: true,
                contentItem: {
                    select: {
                        publishedUrl: true
                    }
                }
            }
        });

        if (!job) {
            return NextResponse.json({ message: "Job not found" }, { status: 404 });
        }

        return NextResponse.json(job);
    } catch (error: any) {
        return NextResponse.json({ message: "Error fetching demo job", error: error.message }, { status: 500 });
    }
}
