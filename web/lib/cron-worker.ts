import prisma from "./prisma";

export async function runCron() {
    console.log("[CRON] Checking for scheduled content...");
    
    const now = new Date();
    
    // Find scheduled content that is due
    const scheduledItems = await prisma.contentItem.findMany({
        where: {
            status: "SCHEDULED",
            scheduledFor: {
                lte: now
            }
        },
        include: {
            website: true
        }
    });
    
    console.log(`[CRON] Found ${scheduledItems.length} items to process.`);
    
    const results = [];
    
    for (const item of scheduledItems) {
        try {
            console.log(`[CRON] Triggering agent for: ${item.title}`);
            
            // In a real server environment, we would use a library like 'bull' or 'qstash'
            // For this MVP, we will hit the existing internal API or call the spawn logic directly.
            // Since we want to keep it simple, we'll use a fetch to the absolute URL of the internal API
            // or better yet, extract the spawn logic to a shared utility.
            // For now, let's assume we hit the API.
            
            const baseUrl = process.env.NEXTAUTH_URL || "http://localhost:3000";
            const response = await fetch(`${baseUrl}/api/run-agent`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-cron-secret": process.env.CRON_SECRET || "default_secret" // Insecure but for MVP
                },
                body: JSON.stringify({ contentId: item.id, internal: true })
            });
            
            if (response.ok) {
                results.push({ id: item.id, status: "triggered" });
            } else {
                results.push({ id: item.id, status: "failed", error: await response.text() });
            }
        } catch (error: any) {
            console.error(`[CRON] Error processing ${item.id}:`, error);
            results.push({ id: item.id, status: "error", error: error.message });
        }
    }
    
    return results;
}
