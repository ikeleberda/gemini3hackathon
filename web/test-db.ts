import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
    try {
        console.log("Attempting to connect to database...");
        const userCount = await prisma.user.count();
        console.log("Connection successful! User count:", userCount);
    } catch (e) {
        console.error("Database connection failed:");
        console.error(e);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

main();
