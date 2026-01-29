import prisma from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST(req: Request) {
    const session = await getServerSession(authOptions);
    const cronSecretHeader = req.headers.get("x-cron-secret");
    const isInternal = cronSecretHeader === (process.env.CRON_SECRET || "default_secret");

    if (!isInternal && (!session || !session.user?.email)) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const { contentId } = await req.json();

        const content = await prisma.contentItem.findUnique({
            where: { id: contentId },
            include: {
                website: {
                    include: {
                        user: true
                    }
                }
            }
        });

        if (!content) return NextResponse.json({ message: "Content not found" }, { status: 404 });

        const user = content.website.user as any;
        const googleApiKey = user.googleApiKey;
        const googleModelName = user.googleModelName;
        const googleFallbackModels = user.googleFallbackModels;

        if (!googleApiKey) {
            return NextResponse.json({
                message: "Google API Key is required. Please add it in Settings."
            }, { status: 400 });
        }

        // Create Job
        const job = await prisma.agentJob.create({
            data: {
                contentItemId: content.id,
                status: "RUNNING",
                logs: "Connecting to backend agent..."
            }
        });

        // Call remote backend
        const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8080";

        console.log(`Calling backend at ${backendUrl}/run for topic: ${content.topic}`);

        // Trigger in background and return immediate response to UI
        (async () => {
            try {
                const response = await fetch(`${backendUrl}/run`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        topic: content.topic,
                        job_id: job.id,
                        db_url: process.env.DATABASE_URL, // Pass the DB URL for direct logging
                        google_api_key: googleApiKey,
                        google_model_name: googleModelName,
                        google_fallback_models: googleFallbackModels,
                        wp_config: {
                            url: content.website.url,
                            username: content.website.username,
                            password: content.website.appPassword
                        }
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Backend error: ${errorText}`);
                }

                const data = await response.json();
                const logs = data.logs ? data.logs.join("\n") : "Workflow completed.";
                const result = data.result || "";

                // Search for URL in BOTH logs AND result (PublisherAgent returns it in result, not logs)
                const combinedOutput = logs + "\n" + result;

                // Update Job
                await prisma.agentJob.update({
                    where: { id: job.id },
                    data: {
                        status: "COMPLETED",
                        logs: logs,
                        currentStep: "Completed"
                    }
                });

                // Update Content Item if successful
                // Primary pattern: [View Post](URL)
                let urlMatch = combinedOutput.match(/\[View Post\]\((https?:\/\/[^\s)]+)\)/);
                // Fallback pattern: SUCCESS: Post published at URL
                if (!urlMatch) {
                    urlMatch = combinedOutput.match(/SUCCESS: Post published at\s*(https?:\/\/[^\s]+)/);
                }
                const publishedUrl = urlMatch ? urlMatch[1] : null;

                const titleMatch = logs.match(/Final Title: (.*)/);
                const publishedTitle = titleMatch ? titleMatch[1]?.trim() : null;

                let finalStatus = "FAILED";
                if (publishedUrl) {
                    // Search combinedOutput (logs + result) since PublisherAgent returns "Saved as Draft" in result, not logs
                    finalStatus = combinedOutput.includes("Saved as Draft") ? "DRAFT" : "PUBLISHED";
                }

                await prisma.contentItem.update({
                    where: { id: content.id },
                    data: {
                        status: finalStatus,
                        publishedUrl: publishedUrl,
                        title: publishedTitle || content.title
                    }
                });

            } catch (error: any) {
                console.error("Backend execution failed:", error);
                await prisma.agentJob.update({
                    where: { id: job.id },
                    data: {
                        status: "FAILED",
                        logs: `Error: ${error.message}`
                    }
                });
            }
        })();

        return NextResponse.json({ message: "Agent started", jobId: job.id }, { status: 200 });

    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error starting agent" }, { status: 500 });
    }
}
