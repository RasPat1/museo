import { NextResponse } from "next/server";
import { getMuseums } from "@/lib/db";

export async function GET() {
    try {
        const museums = getMuseums();
        return NextResponse.json(museums);
    } catch (error) {
        console.error("Museums API error:", error);
        return NextResponse.json(
            { error: "Failed to load museums" },
            { status: 500 }
        );
    }
}
