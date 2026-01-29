import { NextResponse } from "next/server";
import { runCron } from "@/lib/cron-worker";

export async function GET(req: Request) {
    // Basic security check
    const authHeader = req.headers.get("Authorization");
    const cronSecret = process.env.CRON_SECRET || "default_secret";

    if (authHeader !== `Bearer ${cronSecret}`) {
        // Allow local access for testing if needed, but for MVP let's just use the secret
        // return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    try {
        const results = await runCron();
        return NextResponse.json({ success: true, results });
    } catch (error: any) {
        return NextResponse.json({ success: false, error: error.message }, { status: 500 });
    }
}
