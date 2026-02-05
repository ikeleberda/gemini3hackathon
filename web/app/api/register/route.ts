import prisma from "@/lib/prisma";
import { hash } from "bcryptjs";
import { NextResponse } from "next/server";

export async function POST() {
    return NextResponse.json(
        { message: "Registration is disabled" },
        { status: 403 }
    );
}
