
import prisma from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { topic } = await req.json();

        if (!topic) {
            return NextResponse.json({ message: "Topic is required" }, { status: 400 });
        }

        // Create a dummy ContentItem for the demo (no user, no website)
        // This relies on websiteId being optional in the schema
        const content = await prisma.contentItem.create({
            data: {
                title: topic,
                topic: topic,
                status: "DRAFT",
                // No websiteId
            }
        });

        // Create Job
        const job = await prisma.agentJob.create({
            data: {
                contentItemId: content.id,
                status: "RUNNING",
                logs: "Starting demo agent run..."
            }
        });

        // Use a default demo API key (or fallback to system default in backend)
        // For security, strictly this should be server-side controlled.
        // We'll pass empty credentials and let the backend handle it or fail gracefully.
        // Assuming the backend has a fallback key or we use a specific demo key from env.
        const demoApiKey = process.env.DEMO_GOOGLE_API_KEY || process.env.GOOGLE_API_KEY;

        // Call remote backend
        const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8080";

        console.log(`Calling backend for DEMO topic: ${topic}`);

        // Trigger in background
        (async () => {
            try {
                const response = await fetch(`${backendUrl}/run`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        topic: topic,
                        job_id: job.id,
                        db_url: process.env.DATABASE_URL,
                        google_api_key: demoApiKey,
                        google_model_name: process.env.GOOGLE_MODEL_NAME || "gemini-3-flash-preview",
                        wp_config: {
                            url: process.env.DEMO_WP_URL || process.env.WP_URL,
                            username: process.env.DEMO_WP_USERNAME || process.env.WP_USERNAME,
                            password: process.env.DEMO_WP_PASSWORD || process.env.WP_APP_PASSWORD
                        }
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Backend error: ${errorText}`);
                }

                const data = await response.json();
                const logs = data.logs ? data.logs.join("\n") : "Demo completed.";
                const result = data.result || "";

                // Update Job
                await prisma.agentJob.update({
                    where: { id: job.id },
                    data: {
                        status: "COMPLETED",
                        logs: logs + "\n" + result,
                        currentStep: "Completed"
                    }
                });

                // Update ContentItem as fallback if backend didn't do it
                // We'll try to extract the URL from logs if data.published_url isn't there
                const urlMatch = logs.match(/\[View Post\]\((https?:\/\/[^\s)]+)\)/) || 
                                 logs.match(/SUCCESS: Post published at\s*(https?:\/\/[^\s]+)/);
                const publishedUrl = urlMatch ? urlMatch[1] : null;

                if (publishedUrl) {
                    await prisma.contentItem.update({
                        where: { id: content.id },
                        data: {
                            status: "PUBLISHED",
                            publishedUrl: publishedUrl
                        }
                    });
                }

            } catch (error: any) {
                console.error("Demo execution failed:", error);
                await prisma.agentJob.update({
                    where: { id: job.id },
                    data: {
                        status: "FAILED",
                        logs: `Error: ${error.message}`
                    }
                });
            }
        })();

        return NextResponse.json({ message: "Demo agent started", jobId: job.id, contentId: content.id }, { status: 200 });

    } catch (error) {
        console.error(error);
        return NextResponse.json({ message: "Error starting demo agent" }, { status: 500 });
    }
}
